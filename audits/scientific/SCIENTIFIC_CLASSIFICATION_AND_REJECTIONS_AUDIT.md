# Scientific Classification, Spectral Program Disentanglement & Manuscript Caveats Audit

**Milestone 1 — Stage 2 Deep Scientific & Mathematical Audit**  
**Cross-Referenced Sources:** `registry/claims.csv`, `AIEF_1_4_superseded_claims.csv`, `AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md`, `lean/AIEFProofs/AIEFProofs/ControllerFiber.lean`, `Project Histories/Project Lead History 01.pdf`, `04.pdf`, `09.pdf`, `10.pdf`

---

## 1. Why `Artifact Status` and `Evidence Scope` Must Never Be Conflated

Throughout AIEFS's evolution, the single greatest source of overclaiming risk has not been numerical fabrication—the numerical simulations are deterministically seeded and bit-verified—but **scope slippage**: interpreting an exact numerical observation along a finite replay window (`Finite numerical observation`) or an identity conditioned on fixed strict winner inequalities (`Conditional theorem`) as an unconditional global dynamical theorem.

Our registry strictly enforces their separation:

| Artifact / Result | `artifact_status` | `evidence_scope` | What Is Established vs. What Remains Open |
|---|---|---|---|
| `runs/c3da1ac707bf` + `runs/73dca37cf93f` ($N=100$) | `Frozen` | `Controlled experimental result` | Establishes causal sensitivity to `shuffle_R` ($D_B = 0.305909$, $d_z = 8.434$) and `no_mu` ($D_B = 0.271061$) under the AIEF-1.3 protocol. |
| `runs/5a9f093a2fe0` (40 seeds, 7 branches) | `Frozen` | `Controlled experimental result` | Refutes `B` as sole memory bottleneck (`S01`); delayed phase/EMA history reconstructs mature topology after `reset_B`. |
| `test_output/` (40 seeds matched-phase) | `Frozen` | `Controlled experimental result` | Isolates delayed phase/EMA memory from split-time instantaneous phase alignment. |
| `runs/b57562a8ee77` + `Analysis v4` (200 conditions) | `Frozen` / `Supported` | `Controlled experimental result` | Separates physical-time recovery from normalized EMA-window scaling via dual-horizon DID. |
| `ControllerFiber.lean` ($\ker C_{\{2,7\}}$) | `Supported` | `Formalized theorem` | Machine-checks in Lean 4 (`0` `sorry`) that $\ker\begin{pmatrix}1&1&0\\1&0&1\end{pmatrix} = \operatorname{span}\{(1,-1,-1)\}$. Does **not** by itself prove physical winner persistence (`CF12`). |
| `AIEF_1_4_CONDITIONAL_PROPOSAL_EQUALIZATION_THEOREM.md` | `Supported` | `Conditional theorem` | Proves one-sided convergence of selected $K_3$ branch matrices to the analytic family **given** persistent strict winner inequalities and $x_{25}-x_{29}, x_{25}-x_{59} \to 0$. Autonomous infinite-time convergence (`CF11`, `CF12`) remains `Conjecture`. |
| `AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md` | `Exploratory` | `Conditional theorem` | Contains valid kernel algebra (Section 6) alongside an **overstated ambient left-covector claim in Corollary 8.4** (proved explicitly below). |

---

## 2. Disentangling the Spectral & Operator Research Program (Do Not Archive Together)

Per user constraint and primary historical evidence (`Project Lead History 04.pdf`), the AIEF 1.4 spectral/operator investigations split cleanly into **valid full-state / cocycle analyses (`Supported`)** versus **falsified low-dimensional autonomous projections and flawed scans (`Rejected`)**:

### A. Valid & Active Full-State Tangent / Cocycle Work (`Supported` -> `studies/tangent_cocycle_dynamics/`)

1. **`aief_1_4_full_state_tangent_operator.py` & `aief_1_4_history_cocycle_test.py`:** Establish exact finite-step linearization of the delayed update and verify that time-ordered multiplication of the full step Jacobians reproduces perturbation evolution along saved trajectories.
2. **`aief_1_4_branch_tangent_comparison.py`, `aief_1_4_nonlinear_branch_divergence.py`, `aief_1_4_operator_perturbation_decomposition.py`, `aief_1_4_post_switch_divergence_decomposition.py`:** Correctly decompose post-split branch separation across phase, EMA, and admissibility projection channels.
3. **`aief_1_4_jacobian_step_convergence.py` (`aief_1_4_jacobian_step_convergence/`):** Audits exact directional step sizes vs active row-switching margins, directly exposing why naive coarse finite differences fail near ties.

### B. Retired / Falsified Spectral & Motif Scripts (`Rejected` -> `studies/rejected/spectral_compression_and_k3_scan/`)

These nine scripts (and their associated reports) are preserved **unmodified** strictly as negative methodological evidence:

1. **`aief_1_4_operator_compression.py` (`REJ-SPEC-01`):** Projects full non-normal step dynamics onto an 8D POD slow subspace $U_8^\top J U_8$. Because non-normal cross-coupling strongly feeds orthogonal fast directions back into slow coordinates, off-subspace leakage reaches **`24,323.8%`**, invalidating autonomous 8D spectral claims.
2. **`aief_1_4_slow_subspace_projection.py` (`REJ-SPEC-01`):** Unconstrained rollout in the projected slow model diverges catastrophically (`var(slow)/var(full) = 7.5e35`).
3. **`aief_1_4_observable_jacobian.py`, `aief_1_4_augmented_spectrum.py`, `aief_1_4_slow_eigenvector_analysis.py`, `aief_1_4_slow_bundle_geometry.py`, `aief_1_4_multiseed_geometry.py` (`REJ-SPEC-02`):** Use finite-difference step $\varepsilon = 10^{-8}$ across piecewise-linear row-scale winner boundaries whose true tie margin is $4.44 \times 10^{-14}$, conflating boundary-crossing artifacts and transient non-normal amplification with autonomous eigenvalues.
4. **`aief_1_4_coupling_lock_audit.py` (`REJ-LOCK-03`):** Tests $\omega_i + G_i = 0$ in the non-rotating frame rather than the collective mean-frequency rotating frame, misdiagnosing precision cancellation of large terms (`S18`).
5. **`aief_1_4_k3_structure_scan.py` (`REJ-K3-04`):** Enumerates all 3-node triangle subgraphs (`856` subgraphs across 40 seeds, including triangles embedded inside $K_4, K_5, K_6$ cliques) rather than isolated connected components. The corrected component audit (`aief_1_4_k3_fiber_audit/`) shows **`26` true isolated $K_3$ connected components** across the 40 frozen seeds (`Project Lead History 10.pdf, p. 4`).

---

## 3. Mathematical Audit of Draft Manuscript Defect (`Corollary 8.4` in `AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md`)

In `AIEF_1_4_OPERATOR_THEORY_MANUSCRIPT.md` (Section 8, Corollary 8.4), the draft claims that for an equal-capacity component $G$ with clipped controller incidence $C_G$ and kernel basis $V$ ($C_G V = 0$), $V^\top$ acts as a left eigenspace of the ambient Frechet derivative $D\mathcal{A}_\varepsilon(x_G)$ across general fiber points $x_G = x_0 \mathbf{1} + h$ ($h \in \ker C_G$).

### Exact Algebraic Derivation of the Defect

On a strict winner neighborhood where active row sums $q^+ = C_G x_G$ are uniformly clipped to capacity $c$ ($s_k = \frac{c}{q_k^+ + \varepsilon}$ equal across active rows $k$ when $q_k^+$ match), differentiating $\mathcal{A}_\varepsilon(x_G) = s(x_G) \odot x_G$ yields:

$$D\mathcal{A}_\varepsilon(x_G) = s_k I - \frac{s_k}{q^+ + \varepsilon}\, \operatorname{diag}(x_G) C_G^\top C_G.$$

 the **right** action on $V$ vanishes identically for **all** $x_G$ because $C_G V = 0$:

$$D\mathcal{A}_\varepsilon(x_G)\, V = s_k V - \frac{s_k}{q^+ + \varepsilon}\,\operatorname{diag}(x_G) C_G^\top (C_G V) = s_k V.$$

However, multiplying on the **left** by $V^\top$ yields:

$$V^\top D\mathcal{A}_\varepsilon(x_G) - s_k V^\top = -\frac{s_k}{q^+ + \varepsilon}\, V^\top \operatorname{diag}(x_G) C_G^\top C_G = -\frac{s_k}{q^+ + \varepsilon}\,\big(C_G \operatorname{diag}(x_G) V\big)^\top C_G.$$

- **At an edge-uniform base point $x_G = x_{\text{common}} \mathbf{1}$:** $\operatorname{diag}(x_{\text{common}}\mathbf{1}) = x_{\text{common}} I$, so $C_G \operatorname{diag}(x_G) V = x_{\text{common}} C_G V = 0$, and ambient left orthogonality holds! (This explains why scratch scripts `check_01.py` / `check_02.py` passed at the uniform point.)
- **At a general fiber perturbation $x_G = x_0 \mathbf{1} + h$ with $h \in \ker C_G$, $h \neq 0$:** $\operatorname{diag}(h) V \notin \ker C_G$ generically! For the exceptional $K_3$ with $C_{\{2,7\}} = \begin{pmatrix}1&1&0\\1&0&1\end{pmatrix}$ and $v = (1,-1,-1)^\top$:

  $$C_{\{2,7\}} \operatorname{diag}(h)\, v = \begin{pmatrix} h_1 - h_2 \\ h_1 - h_3 \end{pmatrix} = \begin{pmatrix} 2 h_1 \\ 2 h_1 \end{pmatrix} \neq 0 \quad \text{whenever } h = (h_1, -h_1, -h_1)^\top \neq 0.$$

  Hence $V^\top$ is **not** a left eigenvector of $D\mathcal{A}_\varepsilon(x_G)$ on $\mathbb{R}^{|E_G|}$ away from $x_G \propto \mathbf{1}$; instead, one must use the $x_G$-dependent **biorthogonal left covector $u(r)$** derived in the triangular reduction (`CF08`, which itself is pointwise rather than an unconditioned autonomous cocycle dual).

---

## 4. Live Revalidation Summary of Core Empirical Benchmarks

Both primary statistical pipelines were re-executed from scratch on clean `/tmp` outputs during Milestone 1 without touching `runs/`:

1. **AIEF-1.3 Disjoint $N=100$ Paired Ablation (`AIEF_1_3_paired_statistics_updated.py` on `runs/c3da1ac707bf` + `runs/73dca37cf93f`):**
   - `valid_seeds = 100 / 100`, `cohort_seed_overlap = 0` (`CLOSURE PASSED: True`).
   - `shuffle_R`: $\bar{\Delta} D_B = +0.305909$, 95% bootstrap CI $[0.298939, 0.313030]$, $d_z = 8.434$ (reproducing `Project Lead History 01.pdf, p. 539` to 6 decimal places).
   - `no_mu`: $\bar{\Delta} D_B = +0.271061$, $d_z = 4.900$.
   - `no_delay`: $\bar{\Delta} D_B = -0.027424$, $d_z = -0.756$.
   - Saved non-invasively in `audits/scientific/revalidated_summaries/aief_1_3_disjoint_100seed_*`.
2. **AIEF-1.4 Dual-Horizon $T_{\text{window}}$ Analysis v4 (`AIEF_1_4_Twindow_sensitivity_analysis_v4.py` on `runs/b57562a8ee77`):**
   - Completed cleanly in `0.30s` (`exit 0`, `analysis_identity_sha256 = 6e6dea18881adb54...`, `40` seeds, `24` regime groups, `72` DID groups, `12` topology groups, `9,600` event rows, `144` conditional DID groups).
   - Saved non-invasively in `audits/scientific/revalidated_summaries/twindow_v4_*`.
