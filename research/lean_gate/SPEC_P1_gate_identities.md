# Lean work package P1: branch-conditional capacity-gate / controller-kernel identities

Status: NEW unpinned research, branch `research/lean-gate-identities` (from `main` `eb3933c`), 2026-11-09.
P2 (stacked on P1 `dfdb63f`, branch `research/lean-gate-p2`): see §7, which supersedes the P1 statements in §3/§4/§5
where they say "not done", "argued, not proved" or "no separate negation theorem".
Lean project: [`lean/AIEFGateCore`](../../lean/AIEFGateCore). Cross-check: [`lean_gate_crosscheck_v1.py`](lean_gate_crosscheck_v1.py).
Nothing hash-pinned is edited. `registry/claims.csv`, `registry/artifacts.csv` and the ERRATA are not edited.

## 1. What the audit relies on

The rate-law audit (`AI Agent Audits/evidence/scripts/kappa_cycle_kernel.py`, ERRATA E5, and ERRATA
E22 on `main` (landed via PR #18)) measures a one-step multiplier `lam = <(B'(B + δh) - B'(B))/δ, h> / <h, h>` along a
direction `h` in the controller kernel `K = ker A_J`, and compares it with the *state formula* `(1 - γdt) mean(s_J)`.
Its validity rests on an unproved piece of algebra: on a fixed branch, the gate map is affine along `h`, so `lam` does
not depend on `δ`. E22 on `main` (landed via PR #18) also reports an "exact branch formula" `(1 - γdt) Σ h_e² s_ctrl(e)` (exact rational evaluation)
that differs from the state formula by 4.04e-13 on the gap component. P1 proves both facts for the real-arithmetic
model, plus the one-sided K3 statements that `lean/AIEFProofs/README.md` lists as not formalised.

**Status of AUD-RATELAW: it stays UNEXPLAINED.** Nothing in this package changes that. P1 proves one-step,
real-arithmetic, branch-conditional algebra that the audit's estimator relies on; it does not explain the measured
rate law, does not certify any float64 number, and does not touch `registry/claims.csv` or the ERRATA.

## 2. Code being modelled (pinned, read-only)

`aief_experiment_engine_v1.py` `advance_state` (`:755-857`), B part only:

| engine line | code | Lean (`AIEFGateCore/GateMap.lean`) |
|---|---|---|
| `:779` | `R = compute_R(state)` (reads θ, history, EMA; never `B`, ERRATA E5) | `drive : E → ℝ` is a fixed input, `drive = (η+μ)R − μ` |
| `:790-794` | `B + dt*((η+μ)R − μ − γB)` | `pre p drive B e = B e + dt * (drive e − γ * B e)` |
| `:795` | `np.maximum(·, 0)` | `prop = max (pre) 0` |
| `:796-797` | `0.5*(x + xᵀ)`, `fill_diagonal(0)` | implicit: one coordinate per unordered pair `e = (src e, dst e)` |
| `:803` | `row_sum_pre = sum(x, axis=1)` | `incAct G x i = Σ_e A_{ie} x_e` (unsigned incidence) |
| `:804-805` | `pre_violation = min(a − q·row_sum) < delta` | `GateOn p G x := ∃ i, gapA − gapQ * incAct G x i < gapDelta` |
| `:811` | `scale = min(1, capacity/(row_sum + ε))` | `scale p q = min 1 (cap / (q + ε))`, `sc p G x i` |
| `:812-813` | `x * minimum.outer(scale, scale)` | `gated p G x e = x e * min (sc (src e)) (sc (dst e))` |
| `:808-823` | gate applied iff `pre_violation` | `stepB p G drive B = if GateOn … then gated … else prop …` |

`kappa_cycle_kernel.py`: `step_B` (`:52-57`) = one `advance_state` on a clone, i.e. `stepB` on `B + dB`;
controller set `J` (`:73-79`): per edge the endpoint with the smaller scale, both if `|s_i − s_j| ≤ TIE_TOL`;
`A_J` = unsigned incidence restricted to rows `J`; `K = ker A_J` (`nullspace`, SVD). In Lean `IsCtrl p G x ctrl`
says `ctrl e ∈ {src e, dst e}` and `s_ctrl(e) ≤` both endpoint scales (exact; ties allowed, no `TIE_TOL`), and
`InCtrlKer G ctrl h` says `(A h)_{ctrl e} = 0` for every edge, i.e. `h ∈ ker A_J` with `J = range ctrl`.

## 3. Statements formalised (all proved; no `sorry`; axioms only propext, Classical.choice, Quot.sound)

Branch hypotheses used throughout (each is an explicit hypothesis, decided per sample by the cross-check):
(B1) clip: `pre ≥ 0` at `B` and at `B + t h` on every edge with `h_e ≠ 0`; (B2) same gate decision at both
states; (B3) `h ∈ ker A_J`; (B4) the same controller assignment `ctrl` is valid at both states (`IsCtrl`).

**(B3)/(B4) are stronger than the audit's condition.** `IsCtrl` and `InCtrlKer` quantify over *all* edges of the
graph (all 66 edges of the 12-node complete graph in the cross-check): `ctrl e` must be a minimal-scale endpoint of
every edge and `(A h)_{ctrl e} = 0` for every edge. `kappa_cycle_kernel.py` only uses the controller set `J` of the
component being probed and `h ∈ ker A_J` for that `J`. The Lean hypothesis implies the audit's condition (the
component's `J` is contained in `range ctrl`), not conversely. It could be weakened to the edges that matter for
the identity, i.e. edges with `x_e ≠ 0` or `h_e ≠ 0` (an edge with `x_e = h_e = 0` contributes `0` on both sides
whatever its controller); this is not done. In the cross-check the all-edge hypotheses are decided exactly and hold
on 18/20 perturbed samples (all 10 CONTROL, 8/10 GATE; the 2 failures are the branch crossings of N4).

**(B2) is redundant for engine-shaped gates** (`GateMap.lean`, `EngineGate`: `cap·gapQ = gapA − gapDelta`,
`gapQ > 0`, `cap > 0`, `ε > 0`). `gateOn_iff_of_branch` proves that (B3), (B4) and nonnegative proposals force the
same gate decision: the node with `q_k > cap` that fires the gate has scale `< 1`, so if it moved along `h`, the
controller `j` of an edge at `k` with `h_e ≠ 0` has `q_j ≥ q_k` and is unmoved. `stepB_add_smul_of_branch_engine`
is the main theorem without `hon`. Limit: `EngineGate` is the real idealisation (`cap = 19/30` exactly,
`engineGate_ideal`); the float engine's `capacity = 0.6333…` has `cap·q − (a − delta) ≈ −4.2e-17`, so it does not
hold verbatim for the exact-rational transcription of the float config.

1. `stepB_add_smul_of_branch` (main): under (B1)-(B4),
   `stepB (B + t h) = stepB B + t (1 − γdt) · branchScale · h` coordinatewise, exactly, where
   `branchScale e = s_ctrl(e)` at the base proposal if the gate fires, else 1. One-step map is affine along `h`.
2. `multiplier_eq_branch_formula`: for `t ≠ 0` the audit estimator equals `(1 − γdt) Σ branchScale_e h_e² / Σ h_e²`,
   independent of `t` (the "constant multiplier along a kernel direction"). This is the exact branch formula of
   E22 on `main` (landed via PR #18).
3. `stepB_sub_eq_smul_of_uniform`: if `branchScale ≡ s` on `supp h` (all controller scales equal), `h` is an exact
   eigenvector with eigenvalue `(1 − γdt) s` (the state formula).
4. `eventually_clip_gate`: strict clip and a firing gate test at the base persist for all small `|t|` (B1, B2 are
   open conditions). B4 is *not* open at a tie, which is the point of item 6.
5. `K3_gate_component_multiplier` + `K3_gate_branch_sub_state`: for the AUD-RATELAW gap component
   (nodes `[2,7,11] ↦ 0,1,2`, `J = {0,1}`, node 2 not a controller at either state) along `vRay 2 = (1,−1,−1)`
   (= the pinned `vCtrl`), the multiplier is `(1 − γdt)(min s₀ s₁ + s₀ + s₁)/3`, and
   `branch − state = −(1 − γdt)|s₀ − s₁|/6` exactly. This attributes the 4.04e-13 of E22 on `main` (landed via PR #18) to the tied pair's spread.
6. All-tied K3 (`s₀ = s₁ = s₂ = s`), one-sided:
   * `K3_tied_plus_exact`: for `t ≥ 0` (plus clip/gate/positivity) `stepB (B + t vRay c) − stepB B = t(1 − γdt)s · vRay c`;
   * `K3_tied_plus_hasDerivWithinAt`: the right derivative along `+vRay c` is `(1 − γdt) s · vRay c`;
   * `K3_tied_minus_exact`: along `−vRay c` (`τ ≥ 0`, node `c` saturated) node `c` becomes the controller of its two
     edges; their response is `(x_e + τa) · cap/(q_c + 2τa + ε)`, the opposite edge moves by `−τ a s`;
   * `K3_tied_minus_hasDerivWithinAt`: right derivative on an edge at `c` is `(1 − γdt) s (1 − 2x_e/(q_c + ε))`;
   * `K3_tied_minus_not_eigen`: that is `≠ (1 − γdt) s · (−vRay c)_e` when `γdt ≠ 1`, `s ≠ 0`, `x_e ≠ 0`.
   This is the one-sided K3 result listed as not formalised in `lean/AIEFProofs/README.md` ("the gate's directional
   derivative along `+v_c` is `λ₂·v_c` and along `−v_c` is not slow"), proved here for the real model.

## 4. Deliberate abstractions (what the Lean model is NOT)

* **Reals, not float64.** All statements are exact real identities. The engine's float error is outside the model;
  E22 on `main` (landed via PR #18) shows it is the representation error of `fl(B + δH)`. The cross-check bounds model-vs-engine differences by
  evaluating the Lean definitions in exact rationals on the engine's own float inputs (≤ 5.6e-17 absolute here).
* **Edge vectors, not the 12×12 matrix.** Symmetrisation and the zero diagonal are not modelled; one coordinate per
  unordered pair. Equivalence with the matrix form for symmetric zero-diagonal inputs is **argued, not proved**
  in Lean. The evidence is empirical: on 21 engine inputs (the base state and the 20 perturbed inputs
  `fl(B + δH)`, 10 per component) the exact-rational evaluation of the Lean edge-vector definitions agrees with the
  engine's matrix output on all 66 edges to ≤ 5.6e-17 (check F, tolerance 1e-15).
* **One step, `R` fixed.** `drive` is an input. Justified for B-only perturbations within a step by ERRATA E5;
  nothing is said about later steps, phases, delay, the EMA or branch persistence over time.
* **Exact controllers, no `TIE_TOL`.** The audit treats `|s_i − s_j| ≤ 1e-9` as tied; Lean uses exact order.
  In the cross-check the exact controllers on the edges of the K5 control direction are `{0,1,6}`, whereas TIE_TOL treats all five K5 nodes as tied controllers; the identity is unaffected.
* **Lean division `x/0 = 0`.** Irrelevant to the engine (`ε = 1e-12 > 0`); the cross-check transcription copies it.
* **Not formalised:** the closed-form clique multiplier `λ_k = (1 − γdt)c/(c + dt(kη − γc) + ε)` and the
  finite-time departure of the state formula from it (the 3.26e-10 part in E22 on `main` (landed via PR #18)); any TIE_TOL / δ_c selection rule;
  the link between `AIEFGate.G3`/`vRay` and the pinned `AIEFProofs` `src3`/`dst3`/`vRay` (same convention, not
  imported, to keep this project free of path dependencies like `AIEFFreezeCore`).

## 5. Red team

Lean (`AIEFGateCore/RedTeam.lean`, concrete K3: dt = 1/10, γ = 1, cap = 1, ε = 0, drive 0, B = 1):
`nonvacuous_plus` (all hypotheses of item 6 satisfiable; response `(1/20) vRay 2`). Note `nonvacuous_plus` uses
`ε = 0`, unlike the engine (`ε = 1e-12`), and `p0` is not an engine configuration: it shows the hypotheses are
jointly satisfiable in the model, not on engine inputs. Non-vacuity on real engine inputs comes from the Python
cross-check, which decides every hypothesis of `stepB_add_smul_of_branch` exactly and finds them all true on 18/20
perturbed engine samples. Proved negations
`false_drop_kernel` (single-edge direction, B3 dropped: 2/3 vs claimed 1), `false_wrong_constant` (factor `1 − γdt`
dropped), `false_two_sided` (B4 dropped: `+vRay` formula at `t = −1/2` gives 1/4 where the map moves 0),
`false_branch_eq_state` (branch ≠ state formula when `s₀ ≠ s₁`).

Single-hypothesis counterexamples to the main theorem (each is `¬ ∀ …` of `stepB_add_smul_of_branch` on `G3`
with exactly one hypothesis dropped, every other hypothesis holding at the witness):

| theorem | dropped | witness | other hypotheses | failure |
|---|---|---|---|---|
| `false_drop_clip` | `hclip` | `drive = −10`, `B0`, `h = vRay 2`, `t = 1/10`, `ctrl = ctrlPlus 2` | gate off at both, kernel, ctrl | map `0`, claim `9/100` on edge 0 |
| `false_drop_ker` | `hker` | `drive0`, `B0`, `h = e0`, `t = 1`, `ctrl = ![0,0,1]` | clip, gate on at both, ctrl at both | edge 0: `2/3` vs `1` |
| `false_drop_hc0` | `hc0` | `drive0`, `Bc = (1, 6/5, 6/5)`, `vRay 2`, `t = 1/10`, `ctrlPlus 2` | clip, gate, kernel, `hc1` (all tied at `50/99`) | edge 1: `0` vs `−1/22` |
| `false_drop_hc1` | `hc1` | `drive0`, `B0`, `vRay 2`, `t = −1/2`, `ctrlPlus 2` | clip, gate, kernel, `hc0` | edge 1: `0` vs `1/4` |
| `false_drop_hon` | `hon` | `pLow` (gate fires iff some `q_i < 17/10`, `gapQ = −1`), `drive0`, `B0`, `vRay 2`, `t = 1/10`, `ctrlPlus 2` | clip, kernel, ctrl at both | edge 0: `11/20` vs `99/100` |

Honest limit for `hon`: `pLow` is not an engine gate. For engine-shaped parameters no such counterexample exists,
because `hon` is then implied (`gateOn_iff_of_branch`, see §3); the hypothesis is kept in the main theorem because
the theorem is stated for general `Params`.
Mutation check (`lean_mutation_check.py`): five statement mutants of GateMap.lean; all rejected. Inside the script
M1 (drop `hker`), M2 (drop `hc1`), M3 (drop `hclip`) are rejected only by name reference ("Unknown identifier");
each mutated statement is separately refuted by `false_drop_ker`, `false_drop_hc1`, `false_drop_clip`. M4 and M5
(drop the factor `1 − γdt` in the main theorem / the multiplier formula) are rejected semantically (unsolved goals);
a K3 specialisation of M4 is refuted by `false_wrong_constant`; M5 has no separate negation theorem.
Python (`lean_gate_crosscheck_v1.py`): fidelity, hypothesis decisions, zero exact residual, engine agreement and four
kinds of negative control, N1-N4. They are not four independent runs on both components: N1 (wrong constant) and N2
(wrong controller set) are engine-level comparisons against the engine multiplier, evaluated on both components;
N3 (off-fiber direction) and N4 (branch crossing) are exact-arithmetic residual checks on the GATE component only.
N1 is detected on both components. N2 is *enforced on GATE only*: on CONTROL all five nodes are tied to within
float rounding, so "mean scale over all component nodes" coincides with the branch formula (rel. error 1.7e-12)
and `N2_detected = false` there is expected, not a failure; on GATE (node 11 has scale larger by 4.7e-7) it is
detected (rel. error 1.6e-7). See the results JSON.

## 6. Exact Lean statements

```lean
-- AIEFGateCore/GateMap.lean
theorem prop_add_smul_of_clip (drive B h : E → ℝ) (t : ℝ)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e) :
    prop p drive (B + t • h) = prop p drive B + (t * (1 - p.γ * p.dt)) • h
```

```lean
-- AIEFGateCore/GateMap.lean
theorem incAct_add_smul (x h : E → ℝ) (u : ℝ) (i : V) :
    incAct G (x + u • h) i = incAct G x i + u * incAct G h i
```

```lean
-- AIEFGateCore/GateMap.lean
theorem gated_add_smul_of_branch (x h : E → ℝ) (u : ℝ) (ctrl : E → V)
    (hker : InCtrlKer G ctrl h) (hc0 : IsCtrl p G x ctrl) (hc1 : IsCtrl p G (x + u • h) ctrl) :
    gated p G (x + u • h) = fun e => gated p G x e + u * sc p G x (ctrl e) * h e
```

```lean
-- AIEFGateCore/GateMap.lean
theorem stepB_add_smul_of_branch (drive B h : E → ℝ) (t : ℝ) (ctrl : E → V)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)
    (hon : GateOn p G (prop p drive B) ↔ GateOn p G (prop p drive (B + t • h)))
    (hker : InCtrlKer G ctrl h)
    (hc0 : IsCtrl p G (prop p drive B) ctrl)
    (hc1 : IsCtrl p G (prop p drive (B + t • h)) ctrl) :
    stepB p G drive (B + t • h) =
      fun e => stepB p G drive B e +
        t * (1 - p.γ * p.dt) * branchScale p G drive B ctrl e * h e
```

```lean
-- AIEFGateCore/GateMap.lean
theorem multiplier_eq_branch_formula (drive B h : E → ℝ) (t : ℝ) (ctrl : E → V) (ht : t ≠ 0)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)
    (hon : GateOn p G (prop p drive B) ↔ GateOn p G (prop p drive (B + t • h)))
    (hker : InCtrlKer G ctrl h)
    (hc0 : IsCtrl p G (prop p drive B) ctrl)
    (hc1 : IsCtrl p G (prop p drive (B + t • h)) ctrl) :
    (∑ e, (stepB p G drive (B + t • h) e - stepB p G drive B e) / t * h e) / ∑ e, h e ^ 2 =
      (1 - p.γ * p.dt) * (∑ e, branchScale p G drive B ctrl e * h e ^ 2) / ∑ e, h e ^ 2
```

```lean
-- AIEFGateCore/GateMap.lean
theorem stepB_sub_eq_smul_of_uniform (drive B h : E → ℝ) (t s : ℝ) (ctrl : E → V)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)
    (hon : GateOn p G (prop p drive B) ↔ GateOn p G (prop p drive (B + t • h)))
    (hker : InCtrlKer G ctrl h)
    (hc0 : IsCtrl p G (prop p drive B) ctrl)
    (hc1 : IsCtrl p G (prop p drive (B + t • h)) ctrl)
    (hs : ∀ e, h e ≠ 0 → branchScale p G drive B ctrl e = s) :
    stepB p G drive (B + t • h) - stepB p G drive B = (t * (1 - p.γ * p.dt) * s) • h
```

```lean
-- AIEFGateCore/GateMap.lean
theorem eventually_clip_gate (drive B h : E → ℝ) (hpre : ∀ e, 0 < pre p drive B e)
    (hon : GateOn p G (prop p drive B)) :
    ∀ᶠ t in 𝓝 (0 : ℝ),
      (∀ e, 0 ≤ pre p drive (B + t • h) e) ∧ GateOn p G (prop p drive (B + t • h))
```

```lean
-- AIEFGateCore/K3.lean
theorem K3_gate_component_multiplier (t : ℝ) (ht : t ≠ 0)
    (hclip : ∀ e, 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • vRay 2) e)
    (hon : GateOn p G3 (prop p drive B)) (hon' : GateOn p G3 (prop p drive (B + t • vRay 2)))
    (h20 : sc p G3 (prop p drive B) 0 ≤ sc p G3 (prop p drive B) 2)
    (h21 : sc p G3 (prop p drive B) 1 ≤ sc p G3 (prop p drive B) 2)
    (h20' : sc p G3 (prop p drive (B + t • vRay 2)) 0 ≤ sc p G3 (prop p drive (B + t • vRay 2)) 2)
    (h21' : sc p G3 (prop p drive (B + t • vRay 2)) 1 ≤ sc p G3 (prop p drive (B + t • vRay 2)) 2) :
    (∑ e, (stepB p G3 drive (B + t • vRay 2) e - stepB p G3 drive B e) / t * vRay 2 e) /
        ∑ e, vRay 2 e ^ 2 =
      (1 - p.γ * p.dt) *
        (min (sc p G3 (prop p drive B) 0) (sc p G3 (prop p drive B) 1) +
          sc p G3 (prop p drive B) 0 + sc p G3 (prop p drive B) 1) / 3
```

```lean
-- AIEFGateCore/K3.lean
theorem K3_gate_branch_sub_state (a s0 s1 : ℝ) :
    a * (min s0 s1 + s0 + s1) / 3 - a * ((s0 + s1) / 2) = -(a * |s0 - s1| / 6)
```

```lean
-- AIEFGateCore/K3.lean
theorem K3_tied_plus_exact (c : Fin 3) (t : ℝ) (ht : 0 ≤ t) (ha : 0 ≤ 1 - p.γ * p.dt)
    (hcap : 0 ≤ p.cap)
    (hpos : 0 < incAct G3 (prop p drive B) c - 2 * (t * (1 - p.γ * p.dt)) + p.ε)
    (hclip : ∀ e, 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • vRay c) e)
    (hon : GateOn p G3 (prop p drive B)) (hon' : GateOn p G3 (prop p drive (B + t • vRay c)))
    (htie : ∀ i j, sc p G3 (prop p drive B) i = sc p G3 (prop p drive B) j) :
    stepB p G3 drive (B + t • vRay c) - stepB p G3 drive B =
      (t * (1 - p.γ * p.dt) * sc p G3 (prop p drive B) c) • vRay c
```

```lean
-- AIEFGateCore/K3.lean
theorem K3_tied_minus_exact (c : Fin 3) (τ : ℝ) (hτ : 0 ≤ τ) (ha : 0 ≤ 1 - p.γ * p.dt)
    (hcap : 0 ≤ p.cap) (hqpos : 0 < incAct G3 (prop p drive B) c + p.ε)
    (hsat : p.cap / (incAct G3 (prop p drive B) c + p.ε) ≤ 1)
    (hclip : ∀ e, 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + (-τ) • vRay c) e)
    (hon' : GateOn p G3 (prop p drive (B + (-τ) • vRay c)))
    (htie : ∀ i j, sc p G3 (prop p drive B) i = sc p G3 (prop p drive B) j) (e : Fin 3) :
    stepB p G3 drive (B + (-τ) • vRay c) e =
      if G3.src e = c ∨ G3.dst e = c then
        (prop p drive B e + τ * (1 - p.γ * p.dt)) *
          (p.cap / (incAct G3 (prop p drive B) c + 2 * (τ * (1 - p.γ * p.dt)) + p.ε))
      else (prop p drive B e - τ * (1 - p.γ * p.dt)) * sc p G3 (prop p drive B) c
```

```lean
-- AIEFGateCore/K3.lean
theorem K3_tied_plus_hasDerivWithinAt (c e : Fin 3) (ha : 0 ≤ 1 - p.γ * p.dt) (hcap : 0 ≤ p.cap)
    (hpre : ∀ e, 0 < pre p drive B e) (hon : GateOn p G3 (prop p drive B))
    (hqpos : 0 < incAct G3 (prop p drive B) c + p.ε)
    (htie : ∀ i j, sc p G3 (prop p drive B) i = sc p G3 (prop p drive B) j) :
    HasDerivWithinAt (fun t : ℝ => stepB p G3 drive (B + t • vRay c) e)
      ((1 - p.γ * p.dt) * sc p G3 (prop p drive B) c * vRay c e) (Set.Ici (0 : ℝ)) 0
```

```lean
-- AIEFGateCore/K3.lean
theorem K3_tied_minus_hasDerivWithinAt (c e : Fin 3) (hec : G3.src e = c ∨ G3.dst e = c)
    (ha : 0 ≤ 1 - p.γ * p.dt) (hcap : 0 ≤ p.cap)
    (hpre : ∀ e, 0 < pre p drive B e) (hon : GateOn p G3 (prop p drive B))
    (hqpos : 0 < incAct G3 (prop p drive B) c + p.ε)
    (hsat : p.cap / (incAct G3 (prop p drive B) c + p.ε) ≤ 1)
    (htie : ∀ i j, sc p G3 (prop p drive B) i = sc p G3 (prop p drive B) j) :
    HasDerivWithinAt (fun τ : ℝ => stepB p G3 drive (B + (-τ) • vRay c) e)
      ((1 - p.γ * p.dt) * sc p G3 (prop p drive B) c *
        (1 - 2 * prop p drive B e / (incAct G3 (prop p drive B) c + p.ε))) (Set.Ici (0 : ℝ)) 0
```

```lean
-- AIEFGateCore/K3.lean
theorem K3_tied_minus_not_eigen (c e : Fin 3) (hec : G3.src e = c ∨ G3.dst e = c) (a s xe qe : ℝ)
    (ha : a ≠ 0) (hs : s ≠ 0) (hx : xe ≠ 0) (hq : qe ≠ 0) :
    a * s * (1 - 2 * xe / qe) ≠ a * s * (-vRay c e)
```

```lean
-- AIEFGateCore/RedTeam.lean
theorem nonvacuous_plus :
    stepB p0 G3 drive0 (B0 + (1 / 10 : ℝ) • vRay 2) - stepB p0 G3 drive0 B0 =
      ((1 / 20 : ℝ)) • vRay 2
```

```lean
-- AIEFGateCore/RedTeam.lean
theorem false_drop_kernel :
    ¬ ∀ t : ℝ, stepB p0 G3 drive0 (B0 + t • e0) =
        stepB p0 G3 drive0 B0 + (t * (1 - p0.γ * p0.dt) * (5 / 9)) • e0
```

```lean
-- AIEFGateCore/RedTeam.lean
theorem false_wrong_constant :
    stepB p0 G3 drive0 (B0 + (1 / 10 : ℝ) • vRay 2) - stepB p0 G3 drive0 B0 ≠
      ((1 / 10 : ℝ) * (5 / 9)) • vRay 2
```

```lean
-- AIEFGateCore/RedTeam.lean
theorem false_two_sided :
    ¬ ∀ t : ℝ, stepB p0 G3 drive0 (B0 + t • vRay 2) - stepB p0 G3 drive0 B0 =
        (t * (1 - p0.γ * p0.dt) * (5 / 9)) • vRay 2
```

```lean
-- AIEFGateCore/RedTeam.lean
theorem false_branch_eq_state :
    ¬ ∀ a s0 s1 : ℝ, a * (min s0 s1 + s0 + s1) / 3 = a * ((s0 + s1) / 2)
```

Added in the follow-up commit (engine-shaped gate; single-hypothesis counterexamples):

```lean
-- AIEFGateCore/GateMap.lean
structure EngineGate (p : Params) : Prop where
  link : p.cap * p.gapQ = p.gapA - p.gapDelta
  gapQ_pos : 0 < p.gapQ
  cap_pos : 0 < p.cap
  eps_pos : 0 < p.ε
```

```lean
-- AIEFGateCore/GateMap.lean
theorem engineGate_ideal :
    EngineGate ⟨1 / 100, 3 / 200, 19 / 30, 1 / 10 ^ 12, 1, 3 / 2, 1 / 20⟩
```

```lean
-- AIEFGateCore/GateMap.lean
theorem gateOn_iff_of_branch (hp : EngineGate p) (x h : E → ℝ) (u : ℝ) (ctrl : E → V)
    (hx : ∀ e, 0 ≤ x e) (hx' : ∀ e, 0 ≤ (x + u • h) e) (hker : InCtrlKer G ctrl h)
    (hc0 : IsCtrl p G x ctrl) (hc1 : IsCtrl p G (x + u • h) ctrl) :
    GateOn p G x ↔ GateOn p G (x + u • h)
```

```lean
-- AIEFGateCore/GateMap.lean
theorem stepB_add_smul_of_branch_engine (hp : EngineGate p) (drive B h : E → ℝ) (t : ℝ)
    (ctrl : E → V)
    (hclip : ∀ e, h e ≠ 0 → 0 ≤ pre p drive B e ∧ 0 ≤ pre p drive (B + t • h) e)
    (hker : InCtrlKer G ctrl h)
    (hc0 : IsCtrl p G (prop p drive B) ctrl)
    (hc1 : IsCtrl p G (prop p drive (B + t • h)) ctrl) :
    stepB p G drive (B + t • h) =
      fun e => stepB p G drive B e +
        t * (1 - p.γ * p.dt) * branchScale p G drive B ctrl e * h e
```

```lean
-- AIEFGateCore/RedTeam.lean
theorem false_drop_clip : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (GateOn p0 G3 (prop p0 drive B) ↔ GateOn p0 G3 (prop p0 drive (B + t • h))) →
    InCtrlKer G3 ctrl h →
    IsCtrl p0 G3 (prop p0 drive B) ctrl →
    IsCtrl p0 G3 (prop p0 drive (B + t • h)) ctrl →
    stepB p0 G3 drive (B + t • h) =
      fun e => stepB p0 G3 drive B e +
        t * (1 - p0.γ * p0.dt) * branchScale p0 G3 drive B ctrl e * h e
```

```lean
-- AIEFGateCore/RedTeam.lean
theorem false_drop_hon : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre pLow drive B e ∧ 0 ≤ pre pLow drive (B + t • h) e) →
    InCtrlKer G3 ctrl h →
    IsCtrl pLow G3 (prop pLow drive B) ctrl →
    IsCtrl pLow G3 (prop pLow drive (B + t • h)) ctrl →
    stepB pLow G3 drive (B + t • h) =
      fun e => stepB pLow G3 drive B e +
        t * (1 - pLow.γ * pLow.dt) * branchScale pLow G3 drive B ctrl e * h e
```

```lean
-- AIEFGateCore/RedTeam.lean
theorem false_drop_ker : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre p0 drive B e ∧ 0 ≤ pre p0 drive (B + t • h) e) →
    (GateOn p0 G3 (prop p0 drive B) ↔ GateOn p0 G3 (prop p0 drive (B + t • h))) →
    IsCtrl p0 G3 (prop p0 drive B) ctrl →
    IsCtrl p0 G3 (prop p0 drive (B + t • h)) ctrl →
    stepB p0 G3 drive (B + t • h) =
      fun e => stepB p0 G3 drive B e +
        t * (1 - p0.γ * p0.dt) * branchScale p0 G3 drive B ctrl e * h e
```

```lean
-- AIEFGateCore/RedTeam.lean
theorem false_drop_hc0 : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre p0 drive B e ∧ 0 ≤ pre p0 drive (B + t • h) e) →
    (GateOn p0 G3 (prop p0 drive B) ↔ GateOn p0 G3 (prop p0 drive (B + t • h))) →
    InCtrlKer G3 ctrl h →
    IsCtrl p0 G3 (prop p0 drive (B + t • h)) ctrl →
    stepB p0 G3 drive (B + t • h) =
      fun e => stepB p0 G3 drive B e +
        t * (1 - p0.γ * p0.dt) * branchScale p0 G3 drive B ctrl e * h e
```

```lean
-- AIEFGateCore/RedTeam.lean
theorem false_drop_hc1 : ¬ ∀ (drive B h : Fin 3 → ℝ) (t : ℝ) (ctrl : Fin 3 → Fin 3),
    (∀ e, h e ≠ 0 → 0 ≤ pre p0 drive B e ∧ 0 ≤ pre p0 drive (B + t • h) e) →
    (GateOn p0 G3 (prop p0 drive B) ↔ GateOn p0 G3 (prop p0 drive (B + t • h))) →
    InCtrlKer G3 ctrl h →
    IsCtrl p0 G3 (prop p0 drive B) ctrl →
    stepB p0 G3 drive (B + t • h) =
      fun e => stepB p0 G3 drive B e +
        t * (1 - p0.γ * p0.dt) * branchScale p0 G3 drive B ctrl e * h e
```

## 7. P2 (branch `research/lean-gate-p2`, stacked on P1 `dfdb63f`)

Everything below is proved in `lean/AIEFGateCore` with no `sorry`/`admit`/`axiom`; `#print axioms` on every theorem
reports only `propext`, `Classical.choice`, `Quot.sound` (`check_lean_gate.sh` step 7: 237 declarations audited,
110 theorems printed, `disallowed=0`). All P1 theorems keep their exact statements; the P1 main/multiplier/uniform/
engine theorems and `gated_add_smul_of_branch`, `gateOn_of_branch_aux`, `gateOn_iff_of_branch` are now proved as
corollaries of the P2 per-edge versions.

### 7.1 Per-edge controller hypotheses (residual 1 of the P1 review)

`Rel x h e := x e ≠ 0 ∨ h e ≠ 0`; `IsCtrlOn p G S x ctrl` / `InCtrlKerOn G S ctrl h` are `IsCtrl` / `InCtrlKer`
required only for edges `e` with `S e`.

* `stepB_add_smul_of_branch_on`: the P1 main theorem with `hker`, `hc0`, `hc1` required only on `Rel x h`, where
  `x = prop drive B` is the base proposal (the same `Rel x h` for the base and the perturbed controller condition).
  Same conclusion `stepB (B + t h) = stepB B + t(1 − γdt)·branchScale·h`. Proof idea: an edge with `x_e = h_e = 0`
  is `0` on both sides whatever its controller.
* `gated_add_smul_of_branch_on`, `multiplier_eq_branch_formula_on`, `stepB_sub_eq_smul_of_uniform_on`: same weakening.
* `gateOn_iff_of_branch_on` (engine-shaped gate): needs the kernel/controller conditions only on edges with `h_e ≠ 0`;
  `stepB_add_smul_of_branch_engine_on`: engine-shaped main theorem without `hon`, hypotheses on `Rel x h`.
* The edge set cannot be shrunk further (proved, `RedTeam`, on `p0`):
  `false_rel_x_only` (edge set `x_e ≠ 0` alone: `Bx = (0,2,2)`, `h = e0`, `t = 1`; edge 0 maps to `1/3`, claim `1/2`)
  and `false_rel_h_only` (edge set `h_e ≠ 0` alone: `Bh = (2,2,1)`, `h = (1,−1,0)`, `t = 1/10`; on edge 2 the endpoint
  minimum moves, `10/31` vs claim `1/3`).
* `rel_strictly_weaker`: at `Bx = (0,2,2)`, `h = (0,1,−1)`, `t = 1/10`, `ctrl = (0,2,2)` all per-edge hypotheses hold
  and the identity follows, while the all-edge `InCtrlKer G3 ctrl h` is false for **every** controller assignment
  (edge `(0,1)` has `(A h)_0 = 1`, `(A h)_1 = −1`). So the P2 theorem covers cases the P1 theorem cannot.
* Remark, not formalised: on the clip branch `x(B + t h) = x + t(1 − γdt) h`, so for `t(1 − γdt) ≠ 0` the set
  "`x_e ≠ 0` at the base **or** at the perturbed state" equals `Rel x h`. The P1 review note's phrase "edges with
  `x_e ≠ 0` at either state" is therefore right only in that reading; "`x_e ≠ 0` at the base" alone is false
  (`false_rel_x_only`).
* Still stronger than the audit: `IsCtrlOn` asks for a single exact controller per relevant edge valid at both
  states, and `InCtrlKerOn` asks `(A h)_{ctrl e} = 0` on every relevant edge (all 66 edges are relevant when `x > 0`
  everywhere, as in the cross-check). The audit's `J` uses `TIE_TOL`; no Lean statement about `TIE_TOL`.

### 7.2 Engine-shaped non-vacuity with `ε > 0` (residual 2)

`EngineWitness.lean`: `pE = ⟨dt = 1/100, γ = 15/1000, cap = (1 − 5/100)/(3/2), ε = 10⁻¹², a = 1, q = 3/2,
delta = 5/100⟩` (the frozen production values of `aief_experiment_engine_v1.py`, read as exact reals), K3,
`drive = (η + μ)·R − μ` with `η = 0.04`, `μ = 0.03`, `R = 1` (so `1/25`), `B = 8/3` (fixed point of the unclipped
update), `h = vRay 2`, `t = 1/10`, `ctrl = ctrlPlus 2`.
* `engine_nonvacuous`: `EngineGate pE`, `ε > 0`, the gate fires at the base, the scale is binding
  (`sE = cap/(16/3 + 10⁻¹²) < 1`), and every hypothesis of `stepB_add_smul_of_branch_engine_on` holds; the response is
  `stepB(B + t h) − stepB B = (t(1 − γdt)·sE) • vRay 2`.
* `engine_false_no_gamma`: the response is not `(t·sE) • vRay 2`.
Scope: exact reals (the float engine's `capacity` is not exactly `19/30`, see §3 `EngineGate`); a K3 instance with
chosen inputs, not a 12-node engine state reached by a trajectory. `R = 1` is a chosen coherence value, not computed
from phases. This is non-vacuity of the theorem for engine-shaped parameters, nothing more. The value is also pinned by
`tests/test_lean_gate_p2.py` against the independent exact-rational transcription.

Limit of `engine_nonvacuous` (Auditor Seat 002, note N3): it has `x_e ≠ 0` on every edge, so `Rel x h` is all edges
there and it does not exercise the per-edge weakening of §7.1. That is covered by:
* `engine_rel_strictly_weaker` (same `pE`, `ε = 10⁻¹²`): K3, `B = (0, 8/3, 8/3)`, coherence `R = (3/7, 1, 1)` (so
  `drive = (0, 1/25, 1/25)` and `x = (0, 8/3, 8/3)`), `h = RedTeam.hw = (0, 1, −1)`, `t = 1/10`,
  `ctrl = ctrlX = (0, 2, 2)`. Edge 0 has `x_0 = h_0 = 0`; the P1 all-edge `InCtrlKer G3 ctrl hw` is false for every
  controller assignment (`(A hw)_0 = 1`, `(A hw)_1 = −1`), so the P1 theorems cannot be applied; every hypothesis of
  `stepB_add_smul_of_branch_engine_on` holds, the gate fires at both states, and its conclusion follows. This is the
  `ε > 0`, engine-parameter analogue of `RedTeam.rel_strictly_weaker`. Same scope as above (exact reals, chosen K3
  inputs, `R = 3/7` on the empty edge is chosen so that its drive is exactly 0); pinned by
  `tests/test_lean_gate_p2.py::test_engine_rel_strictly_weaker_value`. Its false variant is mutant M10 (§7.3).

### 7.3 M5 negation and a semantic mutation check (residual 3)

* `RedTeam.false_multiplier_no_gamma` (M5) and `RedTeam.false_main_no_gamma` (M4): the multiplier formula / main
  theorem with `(1 − γdt)` dropped are false on `p0`, `B0`, `vRay 2`, `t = 1/10`, `ctrlPlus 2`, where every hypothesis
  holds (estimator `1/2` vs `5/9`; edge 0 `1/20` vs `1/18`).
* `lean_mutation_check.py` has 10 mutants (M1–M5 as before; M6/M7 edge set `x_e ≠ 0` / `h_e ≠ 0` in
  `stepB_add_smul_of_branch_on`; M8 `stepM_eq_stepB` without symmetry; M9 `engine_nonvacuous` without `(1 − γdt)`;
  M10 `engine_rel_strictly_weaker` claiming the all-edge kernel condition holds). A mutant is REJECTED only if all of:
  * (a) build rejection: the mutated file fails to elaborate with the kept proof. For M4–M10 this is a real proof
    failure (type mismatch / unsolved goals); for **M1–M3 it is name-reference only** ("Unknown identifier"), which
    is weak evidence on its own: for M1–M3 the rejection is carried by (b);
  * (b) semantic refutation: the mutated statement, extracted from the mutated source and closed over its section
    variables, is refuted by a proved negation theorem: `theorem aief_refutation : ¬ ∀ …, mutant :=
    fun H => negation (H instance)` elaborates against the built project with no error, the output contains neither
    `declaration uses` nor `sorry`, and `#print axioms aief_refutation` lists only propext / Classical.choice /
    Quot.sound. Negative controls of this validator (Auditor Seat 002, note N1): a `sorry` refutation and a
    refutation through a freshly declared `axiom aief_cheat : False` are both rejected, and the run fails otherwise;
  * (c) term-specificity: the same refutation term applied to the unmutated statement fails to elaborate. This only
    shows that the refutation term depends on the mutation (any type mismatch satisfies it); it is **not** a
    semantic control and adds no evidence beyond (b) (note N2). That the unmutated statements are true is shown by
    the positive control: the unmutated files elaborate with their proofs (and by the full build).
  Result: 10/10 rejected; both validator negative controls rejected.

### 7.4 Matrix form = edge-vector form (residual 4; previously "argued, not proved")

`MatrixForm.lean`: `stepM p D Bm i j` transcribes the engine's matrix B step (`:790-813`: proposal, clip,
`0.5(x + xᵀ)`, zero diagonal, row sums, gate test, `min(s_i, s_j)` gating, zero diagonal) for any finite linearly
ordered node type; `KG V` is the complete graph with edges `i < j`; `toEdge` reads a matrix on edges.
* `stepM_eq_stepB`: for symmetric `Bm` and symmetric drive `D`, `stepM p D Bm i j = stepB p (KG V) (toEdge D)
  (toEdge Bm) ⟨(i, j), _⟩` for every `i < j`.
* `stepM_symm`, `stepM_diag`: the matrix output is symmetric with zero diagonal (so it is determined by its edge values).
* `rowSum_eq_incAct`, `gateOnM_iff`: row sums = unsigned incidence action, matrix gate test ⇔ edge-vector gate test.
* `false_matrix_no_symm`: without the symmetry hypotheses the statement is false (two nodes, `B₀₁ = 1`, `B₁₀ = 0`:
  matrix `9/20`, edge vector `9/10`).
Scope: exact reals; the diagonal of `B` and of the drive is arbitrary (overwritten); symmetry of `B` and of
`R_driver` is a hypothesis (the engine's `B` is symmetric after every step by construction; `R` symmetric is an
engine property not proved here; `shuffle_driver` keeps it symmetric by construction but is not modelled).

### 7.5 Imports (residual 5)

`GateMap.lean` imports 18 specific Mathlib modules instead of `import Mathlib`. Clean `check_lean_gate.sh`:
2032 jobs (was 8712), wall time 26 s (was 6 min 13 s on the same box), still 0 warnings with the Mathlib
style linters active (verified by a temporary over-long line and an unused simp argument, both reported, then removed).

### 7.6 Still open (P2)

* Branch persistence over time and any quantitative branch radius (only small-`t` persistence of clip/gate is proved).
* The closed-form clique multiplier `λ_k`, finite-time departure from it, float64 error, `TIE_TOL`.
* A bridge to the pinned `lean/AIEFProofs` `CCtrl`/`vCtrl` (still re-declared, not imported).
* An engine-shaped counterexample for `hon` cannot exist (P1, `gateOn_iff_of_branch`); the `hon` negation remains on
  the non-engine `pLow`. The P2 red-team negations (`false_rel_*`, M4/M5) use `p0` (`ε = 0`), not engine parameters;
  only the positive witnesses of §7.2 (`engine_nonvacuous`, `engine_rel_strictly_weaker`) are engine-shaped.
* `R` symmetry / `B` symmetry invariance of the engine are hypotheses of §7.4, not theorems.
* **AUD-RATELAW stays UNEXPLAINED.** P2 does not change any label, ERRATA entry or registry claim.
