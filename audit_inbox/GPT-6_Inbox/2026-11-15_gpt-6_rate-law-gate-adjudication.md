# GPT-6 outside-audit review — adjudication of the capacity-gate / controller-kernel rate-law dispute

> **UNVERIFIED INPUT.** This is an outside-agent derivation and reproduction note, not a maintainer finding, registry change, erratum, code change, or owner approval. Researcher 001 / Auditor Seat 002 should independently triage it. The Arena branch is read-only; no Arena files were merged or copied into the repository.

- **Agent / model:** GPT-6
- **Date:** 2026-11-15 (Europe/Tirane)
- **Main reviewed:** `ade1179f049bca0a7de3a1152880a2c6e0a19db4`
- **Main tree:** `757f13e381873b7e067a7f87561034c33e3620b4`
- **Arena branch reviewed:** `arena/d4a487cc-aiefs` at `2af3859eefbec5ced8a434711cdd03ee6c2ade04`
- **Inbox context:** `audit-inbox` at `0be5a2a6241802ea4e56eab4182f51af6bc0b672`
- **Scope:** Independently adjudicate whether Arena Round 10's global direction-preservation experiment invalidates `AUD-RATELAW`; derive the restricted one-step identity from the current engine; identify the exact hypotheses needed; and test both the valid and failure regimes with exact rational arithmetic.
- **Method:** Read-only source inspection of current `main`, read-only inspection of Arena Round 10 and the existing rate-law derivation, plus a standalone `fractions.Fraction` calculation and six unit tests. The candidate mathematical test does not import or execute the AIEF engine. No complete checkout was available locally. No external outreach was performed.

## 1. Bottom-line adjudication

The evidence supports a **split verdict**:

1. **Arena is correct about the global gate form.** The implemented gate is not Miller–MacKay-style global multiplicative enforcement. It applies an endpoint-minimum factor per edge, and arbitrary matrices are generally not rescaled by one common scalar. Arena Round 10's Part A supports that point.
2. **Arena's Part A does not refute `AUD-RATELAW`.** The rate-law claim is not that the gate preserves the direction of every matrix. It is a conditional one-step statement about the gate's action on a particular perturbation subspace, `ker A_J`, when all active controlling scales are equal and the active controller set does not change.
3. **The conditional identity follows directly from the current engine code.** Under the stated assumptions, the per-edge factors collapse to the same component-local scalar `s_J`; a kernel perturbation leaves every controlling row sum unchanged, so it leaves those scales unchanged. The resulting one-step perturbation is exactly multiplied by `(1 - gamma*dt) * s_J`.
4. **Condition (e), equal controlling scales, is essential.** An exact rational K4 example below shows that when controlling scales differ, a vector in `ker A_J` can be mapped outside `ker A_J` by the edgewise gate. This agrees with the limitation already written in `AIEFS_audit_response_3.md` §2.2.
5. **The numerical residual remains unresolved.** This derivation validates the conditional algebraic mechanism, not the reported `~2e-8` replay residual, the full census, or any global convergence claim. The ledger should retain its explicit numerical caveats and the K3 one-sided-ray distinction.

**Recommended disposition:** retain `AUD-RATELAW` as a conditional theorem within its stated scope; do not downgrade it because of Arena Round 10. Separately correct any wording that calls the capacity gate a single-factor multiplicative normalization or implies the Miller–MacKay theorem applies. Tighten the definition of `A_J` in the claim/docs to say explicitly that it is the unsigned incidence restricted to the component's edge set and the controlling rows.

## 2. Source provenance and exact code path

### 2.1 Current main

- `aief_experiment_engine_v1.py`, blob `0d116e83a0d2f6b3f6be0e21d8a730c0aec3b689`:
  - `compute_R`, lines 721–752, reads `state.theta`, `state.history[0]`, and `state.coherence_acc`; it does not read `state.B`.
  - `advance_state`, lines 755–852; `R_physical = compute_R(...)` occurs before the B proposal at line 779. The proposal at lines 790–797 is `B + dt*((eta+mu)*R - mu - gamma*B)`, followed by nonnegative clamp and symmetrization. The capacity gate at lines 803–813 computes `scale = min(1, capacity/(row_sum_pre + eps))` per node and multiplies by `minimum.outer(scale, scale)`.
  - The gate's per-edge factor is therefore `min(s_i, s_j)`, not one global scalar.
- `ERRATA_2026-10-28.md`, blob `bdfa3b3c0eb15d2f15787ef52e0399aedd56a43d`, E5 lines 82–95, independently records the update order and confirms that a B-only perturbation cannot change the R used in that same step. That candidate cause of the residual is ruled out.
- `registry/claims.csv`, blob `f4a775410e516f0b58193457301fe67fd78fadda`, line 50, currently labels `AUD-RATELAW` `Supported` / `Conditional theorem` and lists conditions (a)–(e). The statement already separates the exact state-dependent multiplier from the additional ideal hypotheses needed for the closed form.
- `AI Agent Audits/evidence/scripts/kappa_cycle_kernel.py`, blob `93ae182b8470e9977a5b4367223d40a7b8b75032`, lines 8–18, defines the measurement: a component of `supp(B)`, controlling set `J` as nodes winning or tying for an edge's endpoint minimum, `A_J` as unsigned edge-node incidence restricted to that component's edges and rows `J`, and `K = ker A_J`.
- `AI Agent Audits/AIEFS_audit_response_3.md`, blob `67fdccac4d8664a92516a710beb9a3489258cf72`, §2.2 lines 41–52, states the exact identity and conditions. Lines 108–110 give the scoped wording. This derivation predates Arena Round 10 and is separate from Miller–MacKay's global direction-preservation theorem.

### 2.2 Arena Round 10

- `audits/literature/ROUND_10_FINDINGS.md`, blob `f86a3ba9057317030fe6e8cfbcc1b45affeae834`, on Arena branch `2af3859`:
  - Lines 33–61 apply each enforcement rule to 200 random symmetric nonnegative matrices and measure the angle between `vec(B)` and `vec(B')`. The AIEF gate uses 11 distinct per-edge factors in the median trial and is not proportional to the full vector.
  - Lines 65–89 explicitly scope the simulation comparison as a 12-node all-to-all replica, with `T_SIM=200` versus 800 in the engine, and say it does not measure the AIEF attractor.
  - Lines 98–109 state the global-gate conclusion and its limitations.
- The script `audits/experiments/gate_form/run_gate_form.py`, blob `eaf717d295f8af9d14c3d13c70d3f5654f9860d4`, lines 175–207, confirms Part A uses random symmetric matrices, not perturbations constrained to `ker A_J`.

Arena's measured object is the global comparison `P(B)` versus a scalar multiple of `B`, for generic `B`. `AUD-RATELAW`'s object is instead the restricted directional response `D P(B)[H]` for `H` satisfying `A_J h = 0`, under equal controlling scales and fixed controller selection. These are different mathematical statements.

## 3. Independent derivation from the engine

Fix a connected component `C` of the support graph and let `E_C` be its undirected edge set. Represent a symmetric, zero-diagonal perturbation `H` by its edge vector `h ∈ R^{E_C}`. Let `J` be the set of nodes that attain the minimum endpoint scale on at least one edge in `E_C` (including both endpoints when an edge is tied). Let `A_{J,C}` be the unsigned incidence matrix with rows indexed by `J` and columns indexed by `E_C`.

Write the unprojected proposal as

\[
X(B)=B+\Delta t\big((\eta+\mu)R-\mu-\gamma B\big)
    =(1-\gamma\Delta t)B+F,
\]

where `F` is fixed under a B-only perturbation during this step because the engine computes `R` before updating `B` and `compute_R` does not read `B` (E5). Put `a=1-γΔt`.

For a perturbation `B_ε=B+εH`, while the clamp is inactive,

\[
X(B_\varepsilon)=X(B)+\varepsilon aH.
\]

If `A_{J,C}h=0`, then for each controlling node `i∈J`, its proposal row sum changes by

\[
\varepsilon a\sum_{e\ni i}h_e=0.
\]

Consequently every controlling scale `s_i` is unchanged. If the perturbation is small enough that no untied controller changes (condition (d)), the winning endpoint(s) on each edge remain the same. By definition of `J`, every edge in `E_C` has at least one winning endpoint in `J`. If, in addition, all controlling scales are equal (`s_i=s_J` for every `i∈J`, condition (e)), then for every component edge `e=(i,j)`

\[
\min(s_i,s_j)=s_J.
\]

Thus the entire component receives the same factor on this restricted controller region, even though the global gate is not a homothety on arbitrary matrices. The gated difference is exactly

\[
P_C(X(B_\varepsilon))-P_C(X(B))
  =\varepsilon(1-\gamma\Delta t)s_J H.
\]

This is an exact finite-perturbation identity as long as the stated active-set, positivity and controller-gap conditions remain true; equivalently its restricted one-step multiplier is

\[
\boxed{\lambda=(1-\gamma\Delta t)s_J.}
\]

This derivation does **not** require all node scales in the full network to be equal. It requires only equal scales among the active controlling endpoints for the component, plus a perturbation in the kernel of the incidence restricted to those controlling rows.

### When condition (e) fails

If controlling scales are not equal, define `g_e=min(s_i,s_j)` for each component edge. The restricted response becomes

\[
D P_C[H]_e=(1-\gamma\Delta t)g_e h_e.
\]

The edgewise diagonal multiplication `diag(g_e)` generally does not preserve `ker A_{J,C}` and is not a scalar multiple of `h`. That is exactly why the equal-scale condition is required. The Arena experiment is relevant to this generic nonuniform regime, but not a counterexample to the equal-controller theorem.

## 4. Exact rational tests

The standalone script `exact_gate_fiber_check.py` implements the proposal perturbation and min-endpoint gate using `fractions.Fraction`, including the engine's positive `eps=10^-12`. It uses one four-node complete component with edges `(01,02,03,12,13,23)` and a perturbation

\[
h=(1,-1,0,-1,0,2),\qquad A_{J,C}h=0,\quad J=\{0,1,2\}.
\]

The proposal perturbation factor is `a=99/100` and the finite perturbation magnitude is `δ=1/10000`.

### Case A — equal controlling scales (the theorem's hypothesis)

The base edge weights are `(1,1,1/2,1,1/2,1/2)`. Their row sums are `(5/2,5/2,5/2,3/2)`, so `s_0=s_1=s_2` and node 3 is not a winning endpoint on any edge. Every edge factor is exactly `1000000000000/2500000000001`. The perturbation preserves all three controlling row sums. The exact finite difference equals `a*s_J*h` on every edge and its `A_J` row sums remain zero.

### Case B — unequal controlling scales (the theorem's hypothesis deliberately violated)

The base edge weights are `(3/2,1,1/2,1/4,1/4,1/4)`. Their row sums are `(3,2,3/2,1)` and `J={0,1,2}`, but the three controlling scales differ. The same `h` still satisfies `A_J h=0` and preserves the three controlling row sums. Nevertheless, edge factors differ (`1/(3+eps)`, `1/(2+eps)`, `1/(3/2+eps)` across the active edges), the response is not a common scalar multiple of `h`, and applying `A_J` to the gated response gives nonzero rows at nodes 1 and 2. Thus the kernel is not invariant without condition (e).

**Test result:** 6/6 tests passed. They verify `A_J h=0`, the equal-scale finite-perturbation identity, the unequal-scale failure, and that the global non-proportionality result is compatible with the restricted identity. The output is `exact_gate_fiber_check_results.json`.

These are exact algebraic fixture tests, not a fresh execution of AIEF's full engine or a reproduction of the 374-component census.

## 5. Rate formula scope and numerical caveat

The closed form in `AIEF_audit_response_3.md` §2.2 is a second step, not part of the gate-invariance argument. In addition to the exact one-step conditions, it assumes `R=1` on the component edges and each controlling row sum equals the capacity `c`. With degree `k`, this gives

\[
q_J=(1-\gamma\Delta t)c+k\eta\Delta t,
\qquad
s_J=\frac{c}{(1-\gamma\Delta t)c+k\eta\Delta t+\varepsilon},
\]

and hence

\[
\lambda_k=\frac{(1-\gamma\Delta t)c}
 {c+\Delta t(k\eta-\gamma c)+\varepsilon}.
\]

The `κ_k = kη/c - 1/T_w` expression is the stated `Δt, ε → 0` limit for the corresponding rate difference; it is not an unconditional rate of convergence for the full nonlinear delayed engine.

The current claim and supporting response distinguish:
- 264 resolved components with nonzero two-sided fibers, with their stated λ/κ bounds;
- 110 all-tied K3 components, where `ker A_{K3}=0` and the measured slow directions are one-sided controller-selection rays, not two-sided eigenvectors;
- 32 poorly resolved two-sided components, whose larger errors remain separately scoped;
- the maximum `~2e-8` residual, which remains `UNEXPLAINED` under the predeclared step-size rule in E22.

This adjudication does not change any of those data qualifications. It only resolves the logical relation between the generic per-edge-gate experiment and the conditional controller-kernel identity.

## 6. Recommended wording clarification

A precise, self-contained version of the exact claim would be:

> For a fixed support component `C` with edge set `E_C`, let `J` be the nodes attaining the endpoint-minimum scale on at least one edge of `E_C`, and let `A_{J,C}` be the unsigned edge-node incidence restricted to rows `J` and columns `E_C`. If the gate is active, the proposal clamp is inactive on `C`, a B-only perturbation does not change the within-step `R`, the controller selection is unchanged, and all scales on `J` equal `s_J`, then every perturbation `h` supported on `E_C` with `A_{J,C}h=0` is multiplied exactly by `(1-γΔt)s_J` in one engine step. The closed form `λ_k` additionally assumes `R=1` and row sum `c` at the controlling nodes.

For `AUD-GATE`, use wording such as **“symmetric per-edge min-endpoint capacity scaling”**, and state separately that it is not the single-global-factor multiplicative rule used in Miller–MacKay's theorem. Do not use that global theorem to argue either for or against the conditional kernel multiplier.

## 7. What was not done

- No AIEF engine simulation or 374-component census was rerun; source files were read only.
- No Arena script was executed; its report and source were read only.
- The exact Fraction test is a small independent algebraic fixture, not a proof assistant formalization or production integration test.
- No main files, claim rows, errata, CI workflows, or triage ledger were changed.
- No Arena branch files were merged or salvaged.
- No external outreach was performed.

---

# Appendix A — reproducibility script

`exact_gate_fiber_check.py` (also provided as a separate local file in the handoff package):

```python
#!/usr/bin/env python3
"""Exact-rational checks for the conditional controller-kernel gate identity."""
from __future__ import annotations
from fractions import Fraction as F
from typing import Dict, Iterable, Tuple

Edge = Tuple[int, int]
Edges = Tuple[Edge, ...]
Vector = Dict[Edge, F]
EDGES: Edges = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
J = (0, 1, 2)
H: Vector = {(0, 1): F(1), (0, 2): F(-1), (0, 3): F(0),
             (1, 2): F(-1), (1, 3): F(0), (2, 3): F(2)}
CAP, EPS, A, DELTA = F(1), F(1, 10**12), F(99, 100), F(1, 10_000)

def row_sums(x: Vector) -> Tuple[F, F, F, F]:
    out = [F(0) for _ in range(4)]
    for (i, j), value in x.items(): out[i] += value; out[j] += value
    return tuple(out)  # type: ignore[return-value]

def scales(x: Vector) -> Tuple[F, F, F, F]:
    return tuple(min(F(1), CAP / (q + EPS)) for q in row_sums(x))  # type: ignore[return-value]

def edge_factors(x: Vector) -> Dict[Edge, F]:
    s = scales(x)
    return {e: min(s[e[0]], s[e[1]]) for e in EDGES}

def gate(x: Vector) -> Vector:
    factors = edge_factors(x)
    return {e: x[e] * factors[e] for e in EDGES}

def add_scaled(x: Vector, h: Vector, amount: F) -> Vector:
    return {e: x[e] + amount * h[e] for e in EDGES}

def incidence_rows(h: Vector, nodes: Iterable[int]) -> Dict[int, F]:
    out = {i: F(0) for i in nodes}
    for (i, j), value in h.items():
        if i in out: out[i] += value
        if j in out: out[j] += value
    return out

def fixture_equal_controllers() -> Vector:
    return {(0,1):F(1),(0,2):F(1),(0,3):F(1,2),
            (1,2):F(1),(1,3):F(1,2),(2,3):F(1,2)}

def fixture_unequal_controllers() -> Vector:
    return {(0,1):F(3,2),(0,2):F(1),(0,3):F(1,2),
            (1,2):F(1,4),(1,3):F(1,4),(2,3):F(1,4)}

def evaluate() -> dict:
    report = {}
    for label, base in (("equal_controllers", fixture_equal_controllers()),
                        ("unequal_controllers", fixture_unequal_controllers())):
        perturbed = add_scaled(base, H, A * DELTA)
        d0, d1 = gate(base), gate(perturbed)
        diff = {e:(d1[e]-d0[e])/DELTA for e in EDGES}
        expected_scalar = A * scales(base)[0]
        expected = {e:expected_scalar*H[e] for e in EDGES}
        report[label] = {
            "row_sums_base":[str(v) for v in row_sums(base)],
            "scales_base":[str(v) for v in scales(base)],
            "scales_perturbed":[str(v) for v in scales(perturbed)],
            "edge_factors_base":{f"{i}-{j}":str(edge_factors(base)[(i,j)]) for i,j in EDGES},
            "A_J_h":{str(k):str(v) for k,v in incidence_rows(H,J).items()},
            "gated_difference_over_delta":{f"{i}-{j}":str(diff[(i,j)]) for i,j in EDGES},
            "expected_common_scalar_times_h":{f"{i}-{j}":str(expected[(i,j)]) for i,j in EDGES},
            "A_J_applied_to_gated_difference":{str(k):str(v) for k,v in incidence_rows(diff,J).items()},
            "common_scalar_identity_holds":diff==expected,
        }
    return report

if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
```

# Appendix B — test results

Command:

```
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_exact_gate_fiber_check.py
```

Result:

```text
test_arena_global_direction_counterexample_is_compatible ... ok
test_equal_controllers_give_same_factor_on_every_component_edge ... ok
test_equal_scale_kernel_multiplier_is_exact_for_finite_perturbation ... ok
test_perturbation_is_in_controller_kernel ... ok
test_summary_contains_expected_split ... ok
test_unequal_controller_scales_break_kernel_invariance ... ok

Ran 6 tests
OK
```

Bytecode compilation passed for the script and test module. The full exact-rational output is in `exact_gate_fiber_check_results.json` in the local package.
