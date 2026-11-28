# Lean work package P1: branch-conditional capacity-gate / controller-kernel identities

Status: NEW unpinned research, branch `research/lean-gate-identities` (from `main` `eb3933c`), 2026-11-09.
P2 (stacked on P1 `dfdb63f`, branch `research/lean-gate-p2`): see §7, which supersedes the P1 statements in §3/§4/§5
where they say "not done", "argued, not proved" or "no separate negation theorem".
P3 (branch `research/lean-gate-p3`, from `main` `ba171d0`): see §8 (bridge to the pinned `lean/AIEFProofs` controller
fiber, n-step branch persistence, engine-shaped negations, semantic mutation check); it supersedes the §7.6 items it
closes.
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

## 8. P3 (branch `research/lean-gate-p3`, from `main` `ba171d0`)

Everything below is proved in `lean/AIEFGateCore` with no `sorry`/`admit`/`axiom`/`native_decide`. Clean
`SKIP_CACHE=1 ./check_lean_gate.sh` (2026-11-09): PASS, 2149 jobs, 0 warnings, 439 declarations audited, 239
theorems/lemmas printed with `#print axioms`, `disallowed=0`; every new public theorem depends only on `propext`,
`Classical.choice`, `Quot.sound` (two depend on `propext` alone). No P1/P2 statement changed. Nothing under
`lean/AIEFProofs`, `lean/AIEFProofsKn` or any hash-pinned artifact is edited; `registry/claims.csv`,
`audit_inbox/TRIAGE.md` and the ERRATA are not edited. **AUD-RATELAW stays UNEXPLAINED.**

### 8.1 Bridge to the pinned controller fiber (`CCtrl`, `vCtrl`)

**Route taken: verbatim restatement plus a byte-level check, not a cross-project import.** `check_lean_gate.sh`
step 2 rejects Lake path dependencies for this project (since P1: the gate package depends on Mathlib only, so its
CI job does not build or trust the pinned project's outputs). Importing `lean/AIEFProofs` would mean adding a path
dependency, i.e. loosening that rule, so it was not done. Instead:

* `AIEFGateCore/Pinned/{ControllerFiber,ControllerFiberProjector,ControllerFiberQuotient,CompleteGraphIncidence}.lean`
  are the four pinned modules, compiled again inside `AIEFGateCore`, with exactly these whole-line changes:
  `namespace AIEFProofs` → `namespace AIEFGate`, `end AIEFProofs` → `end AIEFGate`, and the internal imports
  `import AIEFProofs.X` → `import AIEFGateCore.Pinned.X`. Every definition, lemma, proof, comment and blank line is
  otherwise identical (so the restated constants are `AIEFGate.ControllerFiber.CCtrl`, `….vCtrl`,
  `AIEFGate.CompleteGraphIncidence.inc`, `….vRay`, …).
* `tools/ci/check_pinned_restatement.py` (stdlib; re-executes as `python -I -B` like `check_sha256sums.py`) checks:
  the pinned sources have the hard-coded sha256 values, which are also the values listed in
  `lean/AIEFProofs/AIEF_LEAN_SOURCE_SHA256SUMS.txt`; each restated file equals its pinned source after only those
  substitutions (byte for byte, including whitespace and the final newline); `Pinned/` holds no other file. 11
  unittest cases in `tools/ci/tests/test_check_pinned_restatement.py` (run by the `repo-checks` unittest step),
  including negative controls: a wrong `vCtrl` entry in the restatement, a whitespace-only change, an added final
  newline, a renamed namespace line, a changed pinned source with its sums list updated to match (caught by the
  hard-coded pin), an extra file, a missing file, and a shadowing `tools/ci/hashlib.py`.
* **Pass/fail rule change (stricter) with reason:** `check_lean_gate.sh` gains step 2b: if `AIEFGateCore/Pinned`
  exists, `tools/ci/check_pinned_restatement.py` must exist and PASS, else the script fails with exit 2. Reason: a
  restated "pinned" definition is only evidence about the pinned object if the text is verified to be the pinned
  text; without this check a later edit to `Pinned/` would silently turn the bridge into a statement about some
  other matrix. Negative control run locally: changing `| 2 => -1` to `| 2 => 1` in the restated `vCtrl` (and
  regenerating the gate sums) makes `check_lean_gate.sh` fail at step 2 with exit 2.
* **Scope of the binding (limit):** the check is textual and covers the files in `Pinned/` only. It does not stop
  another `AIEFGateCore` file from adding attributes, instances or `simp` lemmas about the restated names. That cannot
  change what the stated bridge theorems say (their statements and the restated definitions are fixed text), but it
  can change how later proofs are found; such additions are not part of the pinned object.

Bridge theorems (`AIEFGateCore/Bridge.lean`, namespace `AIEFGate.Bridge`; `toR` casts a `ℚ` vector to `ℝ`):

| theorem | statement |
|---|---|
| `incCoeff_eq_inc` | for a loopless edge list `(src, dst)`, the gate's `incCoeff i e` equals the pinned `inc src dst i e` (cast) |
| `incAct_toR_eq_mulVec`, `incAct_toR_eq_zero_iff` | the gate's `incAct` on `toR x` is `(inc src dst *ᵥ x)` (cast); full gate kernel ⇔ `inc *ᵥ x = 0` |
| `G3_eq_pinned`, `vRay_eq_pinned` | the gate's `G3` is the pinned `(src3, dst3)`; the gate's `vRay c` is `toR` of the pinned `vRay c` |
| `vRay_two_eq_vCtrl` | the gate's `vRay 2 = toR vCtrl` (through the pinned `vRay_two_eq_vCtrl`) |
| `incAct_G3_ctrlRow` | rows `0, 1` of the gate's incidence action on `toR x` are `(CCtrl *ᵥ x) 0, 1` (through the pinned `inc3_rows_eq_CCtrl`) |
| `CtrlJ01`, `CtrlJ01.forced` | a K3 controller assignment (endpoint per edge) never using node 2 (the audit's `J ⊆ {0,1}`); it forces `ctrl 1 = 0`, `ctrl 2 = 1` |
| `inCtrlKer_iff_CCtrl` | `CtrlJ01 ctrl →` (`InCtrlKer G3 ctrl (toR x)` ⇔ `CCtrl *ᵥ x = 0`) |
| `inCtrlKer_iff_exists_smul_vCtrl` | `CtrlJ01 ctrl →` (`InCtrlKer G3 ctrl (toR x)` ⇔ `∃ a : ℚ, x = a • vCtrl`) (through the pinned `CCtrl_mulVec_eq_zero_iff_exists_smul`) |
| `inCtrlKer_iff_smul_vCtrl` | `CtrlJ01 ctrl →` for every real `h`: (`InCtrlKer G3 ctrl h` ⇔ `∃ a : ℝ, h = a • toR vCtrl`) |
| `sc_ctrl_eq_of_PPerp_eq` | `CtrlJ01 ctrl → PPerp *ᵥ x = PPerp *ᵥ y →` the controller scales of `toR x` and `toR y` agree (through the pinned `CCtrl_eq_iff_PPerp_eq`) |
| `stepB_add_smul_vCtrl` | the main theorem `stepB_add_smul_of_branch` along `a • toR vCtrl` with `hker` discharged by the bridge |
| `false_bridge_wrong_vector` | refuted: the bridge with `vCtrl` replaced by the pinned `vRay 0` |
| `false_bridge_any_ctrl` | refuted: the bridge with `CtrlJ01` weakened to "endpoint per edge" (`ctrl = (0,0,2)`) |

So the kernel hypothesis `hker` of the main gate theorem, for every controller assignment of the audit's gate
component, **is** the pinned `ker CCtrl = ℚ·vCtrl` (and its real span), proved, not asserted.

Limits (blunt): (i) the identity with `lean/AIEFProofs` is by verified source text (same toolchain and Mathlib pin),
not by a kernel-level identity of constants across projects: `AIEFGate.ControllerFiber.CCtrl` and
`AIEFProofs.ControllerFiber.CCtrl` are different Lean constants elaborated from the same text. (ii) K3 only, fixed
edge order `(0,1), (0,2), (1,2)`; the node relabelling `[2, 7, 11] ↦ 0, 1, 2` and the claim that the audit's `J`
is `{0,1}` remain external correspondences, exactly as in the pinned files. (iii) `incCoeff_eq_inc` is general
(any loopless edge list, so also the pinned `src4…src6` lists), but nothing from `lean/AIEFProofsKn` (K12,
`finrank_ker_inc`) is restated or bridged. (iv) The controller-fiber files are re-checked by this project's build;
the pinned project's own `check_lean.sh` is unchanged and still separately required in CI.

### 8.2 Branch persistence over `n` steps

`AIEFGateCore/Persistence.lean` (general `V`, `E`): `UniformBranch p G drive B h t s ctrl` bundles the hypotheses of
`stepB_sub_eq_smul_of_uniform_on` (clip on `supp h`, same gate decision, kernel and controller conditions on
`Rel x h` at both states, one branch scale `s` on `supp h`); `amp p t s k = t ∏_{j<k} (1 − γdt) s_j`.

* `stepB_add_smul_of_uniformBranch`: one step, `stepB (B + t h) = stepB B + (t (1 − γdt) s) • h`.
* `iterate_stepB_add_smul_of_branch`: if `UniformBranch` holds at `(stepB^[k] B, amp k, s k, ctrl k)` for every
  `k < n` (explicit hypothesis: the state stays in the branch region), then
  `stepB^[n] (B + t • h) = stepB^[n] B + amp n • h` exactly.
* `amp_mem_Icc`: `amp k ∈ [0, t]` when every factor `(1 − γdt) s_j ∈ [0, 1]`.

Non-vacuity (`AIEFGateCore/PersistenceWitness.lean`), engine-shaped, gate firing, **every `n`**:
`engine_gated_persistence n`: at `pE` (frozen production parameters as exact reals, `ε = 10⁻¹²`), K3, `R = 1`
(drive `1/25`), `B = 8/3`, `h = vRay 2` (`= vCtrl`, §8.1), `t = 1/10`, `ctrl = ctrlPlus 2`: the gate fires and the
scale is binding (`sP k < 1`) at every step, `UniformBranch` holds for every `k < n`, and the `n`-step identity
follows. The base trajectory stays tied, `stepB^[k] BE = cst (bseq k)` (`iterate_BE`), and the invariant
`2 x_k > cap` is preserved (`inv_step`; margin ≈ 4.5·10⁻⁴ in `x`, from the drive term `dt/25`). Red team:
`false_iterate_no_decay` (the `n`-step statement with `amp n` replaced by `t`) is refuted at `n = 1` on this
instance (mutant M13). Values pinned by `tests/test_lean_gate_p3.py` (exact 4-step response against the
independent transcription; a 10 000-step float check of the invariant margin).

Limits (blunt): the drive is frozen for all `n` (`R` fixed; the engine's `R` moves with the phases, so this is the
`B`-subsystem with frozen coherence, not the engine); the branch hypothesis is assumed, not derived, in the general
theorem; uniform scale on `supp h` is needed (with non-uniform scales the direction changes after one step and this
theorem does not apply, so it does not cover the audit's untied gate component `K3_gate_component_multiplier`); the
witness is the symmetric all-tied K3 `+vRay 2` side with chosen inputs (the `−vRay 2` side leaves the branch,
`K3_tied_minus_not_eigen`); no quantitative branch radius.

### 8.3 Engine-shaped negations (`ε = 10⁻¹² > 0`)

`AIEFGateCore/EngineRedTeam.lean`, all at `pE` with `EngineGate pE`:

| theorem | negated statement (as the toy `RedTeam` version, `p0` → `pE`) | instance |
|---|---|---|
| `engine_false_drop_ker` | main theorem without `hker` | `B = 8/3`, `R = 1`, `h = e0`, `t = 1/10`; edge 1 is `8/3·cap/(16/3+u+ε)`, claim `8/3·cap/(16/3+ε)` |
| `engine_false_drop_hc1` | main theorem without `hc1` | `B = 8/3`, `h = vRay 2`, `t = −1/10`; node 2 becomes the smallest scale |
| `engine_false_drop_clip` | main theorem without `hclip` | `B = 0`, `R = 0` (drive `−3/100`), `h = vRay 2`, `t = 1/1000`; edges 1, 2 clipped, gate off |
| `engine_false_main_no_gamma` | main theorem without `(1 − γdt)` | the `engine_nonvacuous` instance (all hypotheses hold) |
| `engine_false_multiplier_no_gamma` | multiplier formula without `(1 − γdt)` | same; estimator `(1 − γdt) sE`, claim `sE` |

Not done (open): `false_drop_hc0`, `false_rel_x_only`, `false_rel_h_only` at `pE`. Impossible: `false_drop_hon` at
engine-shaped parameters (`hon` is implied there, `gateOn_iff_of_branch`). Same scope as §7.2 (exact reals, chosen
K3 inputs, not engine trajectories).

### 8.4 Mutation check: semantic build rejections, engine refutations, M11–M13

**Pass/fail rule change (stricter) with reason.** Step (a) of `lean_mutation_check.py` now counts a build failure
only if it is a real proof failure; a failure made only of name-reference errors (`Unknown identifier` /
`unknown constant`) no longer counts. Reason: such a failure only shows that the kept proof mentions the deleted
binder; it says nothing about the mutated statement (P2 already called it "weak"). To keep M1–M3 meaningful under
the stricter rule they now weaken the hypothesis to `(hker : True)`, `(hc1 : True)`, `(hclip : True)` instead of
deleting it; `True → P` is the same proposition as `P`, so the mutant is the same statement as "hypothesis dropped",
while the binder name stays in scope and the kept proof must fail on the type (it does: `Application type
mismatch`). M8 is changed the same way (`hD hB := True`): its P2 deletion form failed with eight name errors and one
cascading `rfl` failure, i.e. it was only formally "real". Classifier negative control: the P2 deletion form of M1 is
still elaborated each run and must be classified NAME-REFERENCE ONLY and not counted, else the run fails.

Additionally M1–M5 need a **second** step-(b) refutation at engine parameters (`EngineRedTeam.engine_false_*` at
`pE`), validated exactly like the first (no error, no `declaration uses`/`sorry`, `#print axioms` ⊆ standard),
with its own term-specificity control (c). New mutants: M11 (`inCtrlKer_iff_smul_vCtrl` with the pinned `vCtrl`
replaced by the pinned `vRay 0`; refuted by `false_bridge_wrong_vector`), M12 (same with `CtrlJ01` weakened to
"endpoint per edge"; `false_bridge_any_ctrl`), M13 (`iterate_stepB_add_smul_of_branch` without amplitude decay;
`false_iterate_no_decay`). The `sorry` and `axiom aief_cheat : False` validator negative controls are unchanged.

Result (local, 2026-11-09): positive controls PASS (5 files), both validator negative controls REJECTED, classifier
negative control PASS, **13/13 mutants rejected**, every build rejection a REAL PROOF FAILURE, M1–M5 refuted at both
`p0` and `pE`, RESULT PASS.

### 8.5 Still open (P3)

* Branch persistence with non-uniform scales (the audit's untied gate component), with moving `R`, or with a
  quantitative radius; persistence is only proved conditionally (general) and on one tied engine-shaped instance.
* The closed-form clique multiplier `λ_k`, finite-time departure from it, float64 error, `TIE_TOL`.
* Engine-shaped versions of `false_drop_hc0`, `false_rel_x_only`, `false_rel_h_only` (§8.3).
* The bridge covers K3 / `CCtrl` / `vCtrl` and the general incidence; no bridge to `lean/AIEFProofsKn` (K12).
* The mutation check was not run in CI when P3 landed. Since PR #27 it runs in CI: `.github/workflows/lean.yml`, step "Lean-gate mutation check (AIEFGateCore only)" on the required `AIEFGateCore` row (about 2 minutes locally at P3).
* `R` symmetry / `B` symmetry invariance of the engine remain hypotheses (§7.4).
* **AUD-RATELAW stays UNEXPLAINED.** P3 does not change any label, ERRATA entry or registry claim.

## 9. P4a (branch `research/lean-gate-p4a`, from `main` `b198a77`)

Port of the cycle-002 guarded-capacity content into `lean/AIEFGateCore/AIEFGateCore/Capacity.lean`, restated on
`main`'s definitions (`Params`, `scale`, `EngineGate`, `symM`, `GateOnM`, `stepM`). Nothing under `Pinned/`,
`lean/AIEFProofs*` or any other hash-pinned artifact is edited; `registry/claims.csv`, `audit_inbox/TRIAGE.md` and
the ERRATA are not edited. **AUD-RATELAW stays UNEXPLAINED**; this package does not touch it.

**Credit.** Statements and the shape of the counterexamples come from Researcher 040282 (handle only):
`audit_inbox/2026-11-08_researcher-040282/researcher_040282/cycle_002/GateFoundations.lean` on branch
`audit-inbox`, commit `b18a27d`. That file defines its own `feasible`/`kernel`/`gate`/`rowSum` model; none of those
definitions is copied. Every proof in `Capacity.lean` is written for this project's definitions.
The content was selected by an in-session review of that deposit (Researcher 001, audited CLEAN WITH NOTES by
Auditor Seat 002); the review is not part of this repository and is not a library artifact.

### 9.1 What is proved (all on `Capacity.lean`, namespace `AIEFGate.Capacity`)

`stepM p D Bm = gateM p (symM p D Bm)` (`stepM_eq_gateM`, `rfl`), with
`kernelM p X i j = if i = j then 0 else X i j * min (scale p (row i)) (scale p (row j))` and
`gateM p X = if GateOnX p X then kernelM p X else X` (`GateOnX` is `GateOnM` with `X` for `symM p D Bm`).

| Theorem | Hypotheses (exactly as proved) | Source statement (cycle 002) |
|---|---|---|
| `kernel_row_le_cap` | `X ≥ 0`, `0 ≤ cap`, **`0 ≤ ε`** | `kernel_feasible` (ε ≥ 0 version, Researcher 001's relaxation) |
| `kernel_row_upper`, `kernel_row_lower`, `kernel_le_input`, `kernel_nonneg`, `kernel_symm` | `X ≥ 0`; `0 ≤ cap`, `0 ≤ ε` where `scale ≥ 0` is used; zero diagonal for `kernel_row_lower` | `kernel_row_upper/lower`, `kernel_le_input`, `kernel_nonneg`, `kernel_symmetric` |
| `gateOnX_iff` | `EngineGate p` | (new; `GateOnM` ⇔ some row sum `> cap`) |
| `gateM_feasible` | `EngineGate p` (so `0 < ε`, `0 < cap`, link, `0 < gapQ`), `X ≥ 0` | `gate_feasible` (needs `0 < ε`) |
| `gateM_fixes_feasible`, `gateM_idempotent` | `EngineGate p` (`X ≥ 0` for idempotence) | `gate_fixes_feasible`, `gate_idempotent` |
| `gateM_nonneg`, `gateM_le_input`, `gateM_symm`, `gateM_diag` | as named (`EngineGate` not needed) | `gate_nonneg`, `kernel_le_input`, `gate_symmetric`, `gate_zero_diag` |
| `gateM_sub_of_rowSum_eq` | equal row sums, zero diagonals | `gate_difference_of_rowSum_eq` |
| `stepM_row_le_cap`, `stepM_nonneg`, `gateM_stepM` | `EngineGate p`; **no symmetry hypothesis on `D`, `Bm`** | (new, on `stepM`) |
| `preM_eq_convex`, `symM_eq_convex`, `stepM_eq_gateM_convex` | `γ ≠ 0` | port bridge to the cycle-003 proposal form. Despite the names these are **affine** identities: the weights `1 − γdt`, `γdt` are a convex pair only when `0 ≤ γdt ≤ 1` (`convex_weights_iff`, `preM_between`, PR #27). Names kept for the port. |

The `0 < ε` / `0 ≤ ε` scope is exactly what is proved: `0 ≤ ε` for the kernel row bound only; everything that
involves the guard goes through `EngineGate`, hence `0 < ε`. "`0 < ε` can be relaxed" is **not** claimed in general.

`AIEFGateCore.Capacity.scale_nonneg` and `scale_le_one` reuse the names of the `pE`-only lemmas in `PersistenceWitness.lean` (`:85`, `:90`), in a different namespace, so the names do not clash. The `Capacity` versions generalise those: they hold for any `p` with `0 ≤ cap` and `0 ≤ ε` (`scale_le_one` holds for any `p`).

The port bridge states that `stepM` is the gate of the symmetrised clip of `(1 - γ dt) B + γ dt (D/γ)`. The
statement `stepM = weightStep` of Researcher 040282's model (which needs `EngineGate`, `0 < γ`, symmetric `D`, `B`;
`false_matrix_no_symm` refutes it without symmetry) is *not* in the library: it would need their definitions.

### 9.2 Negations and non-vacuity (`Fin 2`, `Xo a` = off-diagonal `a`; at `pE`, `ε = 10⁻¹²` unless noted)

`false_kernel_fixes_boundary`, `false_kernel_idempotent` (the unguarded kernel moves/does not fix the boundary
`row = cap`; `gateM_Xo_boundary`: the strict guard fixes it), `false_gate_nonexpansive` (a jump of size `~ε` at the
boundary against an input change of `10⁻¹⁵`), `false_fixes_without_feasible`, `false_row_lt_cap`,
`false_le_reversed`, `false_diff_without_equal_rows`, `false_kernel_lower_no_hyp`, `false_gateM_symm_no_hs`,
`false_kernel_row_no_eps` (`pN`: `cap = 1`, `ε = -1/2`; kernel row `3/2 > cap`), `false_gateM_feasible_no_link` and
`false_stepM_row_no_link` (`pB`: `cap = 1/2` against guard threshold `1`; not `EngineGate`),
`witness_gate_active` (gate fires on `Xo 1`, output `< cap`, `≠` input), `witness_gate_inactive`,
`witness_stepM_active` (drive `Xo 100`, `B = 0`, proposal `Xo 1`, gate fires).

### 9.3 Mutation check: M14–M23

`lean_mutation_check.py` now has 23 mutants; M14–M23 each weaken or alter one statement of `Capacity.lean`
(`ε`-hypothesis to `True`, idempotence for the unguarded kernel, feasibility to `True`, strict capacity bound,
reversed inequality, equal-row-sums to `True`, scale hypothesis to `True`, symmetry to `True`, `EngineGate` to `True`
for `gateM_feasible` and for `stepM_row_le_cap`), and each must pass the same three tests as M1–M13
(real proof failure; refuted by the proved `false_*` theorem with standard axioms only; term-specificity). M14, M22
and M23 are refuted at `pN`/`pB` (the hypothesis in question is a parameter condition `pE` satisfies); the rest at `pE`.

Result (local, 2026-11-10): positive controls PASS (6 files), both validator negative controls REJECTED, classifier
negative control PASS, **23/23 mutants rejected**, every build rejection a REAL PROOF FAILURE (type mismatch,
`simp` made no progress, invalid field on `True`), each refuted by a proved negation with standard axioms only, each
term-specific, RESULT PASS. The first run of M14-M23 had 3 mutants whose refutation term did not elaborate (an
underdetermined `by norm_num` and a missing `open`); that is a defect of the new refutation terms, fixed in the
script, and no mutant, statement or proof was changed to make it pass.

### 9.4 Gate results (local, 2026-11-10, Europe/Tirane)

* `SKIP_CACHE=1 ./check_lean_gate.sh`: PASS, 2150 jobs, 0 warnings, 15 source files, 512 declarations audited
  (439 before; `Capacity.lean` has 58 theorems and 9 defs, plus 6 auto-generated `eq_1` lemmas), `disallowed=0`;
  every `Capacity` declaration depends only on `propext`, `Classical.choice`, `Quot.sound`. No `sorry`/`admit`/
  `native_decide`/user `axiom`/`unsafe`/`implemented_by`/`extern` (step 6: 0 hits). Two build iterations were
  needed to clear Mathlib style-linter warnings (line length, 7 then 1), no proof changed.
* `lean_mutation_check.py`: 23/23 (above). `research/lean_gate/tests`: 40 passed (`test_lean_gate_p4a.py` pins the
  witness values against an independent exact-rational transcription and the M14-M23 shape).

### 9.5 Still open (P4a)

* Not ported: the cycle-004 phase/delay content (no theorem there depends on `phaseInput`'s argument; review §4.3),
  the four `rat_*` counterexamples are ported only as `Fin 2` matrix witnesses, not as the 12-node engine state.
* No trajectory statement: one step, exact reals, chosen `Fin 2` inputs; nothing about float64 or `TIE_TOL`.
* The gate is not nonexpansive (`false_gate_nonexpansive`); no Lipschitz bound is claimed.
* The mutation check was not run in CI when P4a landed. Since PR #27 it runs in CI (see §8.5; about 5 minutes locally at P4a).
* **AUD-RATELAW stays UNEXPLAINED.**


## 10. P4b (branch `research/lean-gate-p4b`, from `main` `3c5c0ef`, which contains P4a)

Port of the cycle-003 weight-update bridge into `lean/AIEFGateCore/AIEFGateCore/WeightUpdate.lean` (namespace
`AIEFGate.WeightUpdate`) and `Freeze.lean` (namespace `AIEFGate.Freeze`), restated on `main`'s definitions (`Params`,
`scale`, `EngineGate`, `symM`, `rowM`, `stepM`, and `Capacity.gateM/appliedFactor`). Nothing under `Pinned/`,
`lean/AIEFProofs*`, `lean/AIEFFreezeCore` or any other hash-pinned artifact is edited; `registry/claims.csv`,
`audit_inbox/TRIAGE.md` and the ERRATA are not edited. **AUD-RATELAW stays UNEXPLAINED**; this package does not touch it.

**Credit.** Statements come from Researcher 040282 (handle only):
`audit_inbox/2026-11-08_researcher-040282/researcher_040282/cycle_003/GateProposalBridge.lean` on branch `audit-inbox`,
commit `b18a27d`. Its `weightStep`/`proposal`/`gate` model is not imported or copied; every proof here is written for this
project's definitions. The selection and the corrections (drop `hf0`, add `trajectory_symmetric`, N = 12 threshold) come from
Researcher 001's review of that deposit (audited CLEAN WITH NOTES by Auditor Seat 002); the review is not a library artifact.

### 10.1 `Freeze.lean` (scalar core)

`AIEFGateCore` may not have path dependencies (step 2 of `check_lean_gate.sh`), so it cannot import
`AIEFFreezeCore`. `Freeze.lean` restates its five scalar statements (`upper_geom`, `eventually_off`, `eventually_on`,
`edge_eventually_off`, `edge_eventually_on`) with the same statements; `test_lean_gate_p4b.py` checks the statements agree
textually with `lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean`. New: the additive-drive forms `edge_off`, `edge_on`
(`B⁺ = λ max 0 ((1 - h) B + d)`, no division by `h`), derived from the u-forms.

### 10.2 What is proved (`WeightUpdate.lean`; `B`, `D` symmetric, `B ≥ 0` where noted)

| Theorem | Hypotheses (exactly as proved) | Content / source statement (cycle 003) |
|---|---|---|
| `rowM_le_upper` | `B ≥ 0`, `B`,`D` symmetric, `0 ≤ dt`, `γ dt ≤ 1` | `rowM ≤ (1-γdt) rowS B + dt · pdriveRow D` (`proposal_row_upper`) |
| `rowM_le_envelope` | as above, `rowS B ≤ cap`, `pdriveRow D i ≤ S` | `rowM ≤ (1-γdt) cap + dt S` (`proposal_row_upper_of_feasible`) |
| `stepM_scalar_recurrence` | `B`,`D` symmetric, `i ≠ j` | `stepM_ij = appliedFactor · max 0 ((1-γdt) B_ij + dt D_ij)` (`weightStep_scalar_recurrence`) |
| `appliedFactor_lower` | `EngineGate p`, `X ≥ 0`, `rowS X i ≤ Mi`, `rowS X j ≤ Mj` | factor `≥ scale (max Mi Mj)` (`appliedFactor_lower_of_row_uppers`) |
| `stepM_factor_lower` | `EngineGate p`, `0 ≤ dt`, `γ dt ≤ 1`, `B ≥ 0` symmetric and feasible, `D` symmetric, drive-row bounds | factor `≥ edgeFloor` (`weightStep_factor_lower_of_drive_bounds`) |
| `good_step` | `EngineGate p`; none on `D`, `B` | `stepM` output is `Good` (nonneg, symmetric, zero diagonal, row sums `≤ cap`) |
| `trajectory_symmetric`, `trajectory_zero_diag`, `trajectory_nonneg` | `B 0` symmetric / zero diagonal / `≥ 0`; `EngineGate p` for `nonneg` | **new**: the source assumes symmetry, here `B` stays symmetric and zero-diagonal |
| `trajectory_feasible_from_first` | `EngineGate p`; none on `B 0` | `trajectory_feasible_from_first` |
| `trajectory_good_of_start` | `EngineGate p`, `Good (B 0) ∨ 1 ≤ T` | `trajectory_good_of_start` (H0) |
| `edge_eventually_off_from`, `edge_eventually_off` | `EngineGate p`, `0 < dt`, `0 < γ`, `γ dt < 1`, `D` symmetric, `D_ij ≤ U`, `0 ≤ U < γ B_c`; start `Good (B 0) ∨ 1 ≤ T` (`_from`); **no hypothesis on `B 0`** (`edge_eventually_off`) | `adaptive_edge_eventually_off(_from)` |
| `edge_eventually_on_from`, `edge_eventually_on` | as OFF, drive rows `≤ Si, Sj`, `D_ij ≥ L ≥ 0`, `B_c < κ dt L/(1 - κ(1-γdt))`, `κ = edgeFloor`; **no `hf0`, no hypothesis on `B 0`** (`edge_eventually_on`) | `adaptive_edge_eventually_on(_from)` (source needs `hf0`, redundant) |
| `onGap_iff` | `0 ≤ S`; at `pE`, `L = 1/25`, `B_c = 3/25` | `3/25 < onGap S ↔ S < 18999999991/90000000000` |
| `onGap_N12_fails`, `onGap_N12_value`, `onGap_five_neighbours`, `onGap_six_neighbours_fail` | none | N = 12 coarse envelope `S = 11/25` fails (`0.0575 < onGap < 0.0576`); 5 maximally driven neighbours hold; 6 fail |

**Exact threshold proved:** at `pE` (`dt = 1/100`, `γ = 3/200`, `cap = 19/30`, `ε = 10⁻¹²`), maximal drive `D = 1/25`
(`η = 0.04`, `R = 1`; `u = D/γ = 8/3`) and `B_c = 3/25`, the ON hypothesis holds iff the positive-drive-row bound is
`S < 18999999991/90000000000` (`= 0.2111…`, `19/90 - 10⁻¹⁰`; `5.2777…` times the maximal drive; `S/γ < 14.0740…` in `u`
units; the review's "≈ 14.07 = 5.28 L" is this value rounded). At `N = 12`, `S = 11/25`: it fails (`onGap ≈ 0.0576`).
This is about the hypothesis of `edge_eventually_on`, not a statement that ON fails.

**Statement changes against the source:** no division by `γ` (drive `D`, proposal `preM = (1-γdt)B + dt D`; `0 < γ`, `0 < dt`,
`γ dt < 1` explicit; the engine validates only `γ ≥ 0`, so `γ = 0` and `γ dt ≥ 1` are engine-legal but not covered);
`EngineGate p` instead of `0 < ε`, `0 ≤ c`; `hf0` and `hB0` dropped from the ON/OFF theorems (one step already gives a `Good`
matrix); the per-node capacity vector of the source is the scalar `cap` of `Params`.

**ε scope.** Exactly as proved: every gate statement here uses `EngineGate p`, hence `0 < ε`. The only `0 ≤ ε` result is
`Capacity.kernel_row_le_cap` (P4a). Nothing is claimed for `ε ≤ 0`.

### 10.3 Negations and non-vacuity (`Fin 2`; `pE` unless noted)

`false_rowM_upper_no_hh1` (`pH`, `γ dt = 2`), `false_recurrence_no_symm`, `false_factor_lower_no_rowbound`,
`false_factor_lower_no_drivebounds`, `false_trajectory_symmetric_no_start`, `false_trajectory_diag_no_start`,
`false_trajectory_nonneg_no_start`, `false_good_no_start` (and `witness_trajectory_not_good_at_zero`: not `Good` at 0,
`Good` after one step), `false_off_no_gap(_from)` (the ON instance violates the OFF gap), `false_on_no_gap(_from)` (the OFF
instance violates the ON gap), `false_gap_at_threshold` (strictness of `onGap_iff`); non-vacuity:
`witness_on_instance` (all hypotheses of `edge_eventually_on` discharged at `pE`, **engine `B_c = 3/25`**, `Si = Sj = L = 1/25`,
`B 0 = 0`; conclusion `3/25 < B_n(0,1)` eventually) and `witness_off_instance` (`B 0 = 1/5 > 3/25`, `U = 1/1000 < γ B_c`;
conclusion `B_n(0,1) < 3/25` eventually). Not claimed: that the coupled engine produces such drive sequences.

### 10.4 Mutation check: M24–M36 (13 new mutants, 36 total)

M24 `rowM_le_upper` (`γ dt ≤ 1` to `True`), M25 `stepM_scalar_recurrence` (`B` symmetric to `True`), M26 `appliedFactor_lower`
(row bound to `True`), M27 `stepM_factor_lower` (both drive bounds to `True`), M28–M30 `trajectory_symmetric/zero_diag/nonneg`
(`B 0` hypothesis to `True`), M31 `trajectory_good_of_start` (`hstart` to `True`), M32–M35 `edge_eventually_off(_from)` and
`edge_eventually_on(_from)` (gap hypothesis to `True`), M36 `onGap_iff` (`<` to `≤`). Same three tests as M1–M23. Rule changes (written
reason): (i) `OPENS` of the refutation file additionally opens `MatrixForm.symM/rowM` and `WeightUpdate.pdriveRow/edgeFloor/Good/onGap/Sstar`
so that the closed statements of the new mutants elaborate (no acceptance criterion changed); (ii) an optional environment variable
`AIEF_MUT_ONLY` (regex on mutant names) restricts a debugging run; the recorded run is the full one. The first full run had 8 of the 13 new mutants
with refutation terms that did not elaborate (missing `open`s, one unsolved `norm_num`); this was a defect of the new terms, fixed in the script;
no mutant, statement or proof was changed to make it pass. Mutation-count pin: `test_lean_gate_p4b.py` pins the exact count (36); the
P4a test now asserts `>= 23`.

### 10.5 Gate results (local, 2026-11-10, Europe/Tirane)

* `SKIP_CACHE=1 ./check_lean_gate.sh`: PASS, 2152 jobs, 0 warnings, 17 source files, **599 declarations audited** (512 before),
  every one depending only on `propext`, `Classical.choice`, `Quot.sound`; step 6: 0 hits.
* `lean_mutation_check.py` (full run): positive controls PASS (7 files), both validator negative controls REJECTED, classifier
  negative control PASS, **36/36 mutants rejected** (M1-M23 unchanged, M24-M36 new, none survived), every build rejection a REAL PROOF
  FAILURE, each refuted by a proved negation with standard axioms only, each term-specific.
* `research/lean_gate/tests`: 50 passed (`test_lean_gate_p4b.py`: 10 tests pinning the threshold, N = 12 / five / six neighbours,
  the `Freeze.lean` statements against `FreezeCore.lean`, banned markers, credit by handle, exact mutant count 36).

### 10.6 Still open (P4b)

* Drive sequences satisfying the band hypotheses are not shown to arise from the coupled engine; the coarse `(N-1)·D` envelope does not
  certify ON at `N = 12` (`onGap_N12_fails`); a sharper row-sum bound is needed.
* `γ = 0` and `γ dt ≥ 1` (engine-legal) are outside the edge theorems; float64, phases, delay and the EMA are not modelled.
* No Lean-side statement pin (Lea-style statement hash) in CI yet.
* **AUD-RATELAW stays UNEXPLAINED.**


## 11. P5 (branch `research/lean-gate-p5`, written from `main` `3c5c0ef`, which contains P4a; merge-refreshed on 2026-11-11 onto `main` `1c30ca5`, which contains P4b (PR #26) and the #27 follow-ups, see §11.7)

Port of Researcher 040282's cycles 010 (`HistoryBuffer`), 011 (`PhaseIncrement`) and 013 (`PhaseCoherenceBridge`) into
`lean/AIEFGateCore/AIEFGateCore/{HistoryBuffer,PhaseIncrement,PhaseCoherence}.lean` (namespaces `AIEFGate.History`,
`AIEFGate.Phase`, `AIEFGate.PhaseCoherence`), with the fixes required by Auditor Seat 002. Nothing under `Pinned/`,
`lean/AIEFProofs*`, `lean/AIEFFreezeCore`, `Capacity.lean`, `.github/` or any other hash-pinned artifact is edited;
`registry/claims.csv`, `audit_inbox/TRIAGE.md` and the ERRATA are not edited. **AUD-RATELAW stays UNEXPLAINED**; this
package does not touch it.

**Credit.** Statements and proofs come from Researcher 040282 (handle only). Cycles 010/011: `audit_inbox/2026-11-08_researcher-040282/researcher_040282/cycle_010/proposal/HistoryBuffer.lean`
(md5 `fe47db36…`, identical copy in cycle 011) and `cycle_011/proposal/PhaseIncrement.lean` (md5 `b26f225f…`) on branch `audit-inbox`, commit
`1b5ae52`. Cycle 013: `PhaseCoherenceBridge.lean`, md5 `410275adc4ea837a6384cefe2d545c2d`; **this file is not on `audit-inbox`** (the owner
supplied it; the auditor's built copy is the reference). The deposit sources are not imported: `AIEFGateCore` may have no path dependency
(step 2 of `check_lean_gate.sh`) and the files import `HistoryBuffer`/`PhaseIncrement` by bare module name, so the three files are restated inside
the project (namespace, imports and docstrings changed; statements and proofs otherwise as deposited). Because the deposit is not on `main`, there
is nothing to compare textually against in the repository (unlike P4b's `FreezeCore.lean`): `test_lean_gate_p5.py` records the whitespace-normalised
deposit statements (6 for 010/011, 17 for 013) with the md5s above and checks that the restated statements agree. Audited by Auditor Seat 002
(010 ADOPT, 011 ADOPT AS BUILDING BLOCK, 013 ADOPT WITH NOTES); the selection and the fixes follow that audit.

**Overlap with `main`'s definitions.** `coherenceTrace`/`reported`/`sourceDrive` feed `main`'s `MatrixForm.preM`/`stepM` (`main_preM_source_formula`,
`main_phase_preM` are `rfl`); new: `sourceDrive_symm` and `main_phase_stepM_eq_stepB` discharge the symmetric-drive hypothesis of
`MatrixForm.stepM_eq_stepB` for the phase-specific drive, so the matrix step with that drive equals the edge-vector step `stepB`.
`History`/`Phase` overlap nothing in `main` (no phase or delay state yet); the engine convention is a source-convention extension.

### 11.1 What is proved

| Theorem | Hypotheses (exactly as proved) | Content |
|---|---|---|
| `History.historyTrace_index`, `_oldest`, `_newest` | none | slot `i` at read `n` holds `x (n + i - D)` (constant prehistory); oldest `x (n - D)`; newest `x n` |
| `Phase.phasor_wrap` | none | `phasor (wrapPhase t) = phasor t` |
| `Phase.delayed_input_step` | none | `z_{n+1} = z_n · phasor (u n i − delayedIncrement d u n j)`; `delayedIncrement = 0` for `n < D`, `u (n−D) j` else. The offset `(ω_i+ω_j)/2·τ` **cancels**: this theorem does not pin it |
| `Phase.delayed_input_chord_bound` | none | `‖z_{n+1} − z_n‖ ≤ |u n i − delayedIncrement d u n j|` (circular chord) |
| `PhaseCoherence.input_engine_convention` | none | `coherenceInput = exp(i (θ_n,i − θ_{n−D},j − (ω_i+ω_j)/2 · τ))` with the **read-time `n − D`** index; this is what pins the offset and the delay index |
| `input_norm`, `innovation_engine_convention`, `lateSource_startup`, `innovation_transport` | none | unit modulus; `C_{n+1} − αC_n = (1−α) exp(i dphi)`; startup clock; transport of the innovations by `phasor (u n i − lateSource d u n j)` |
| `coherenceTrace_unitDisk` | `0 ≤ α ≤ 1`, `‖C0‖ ≤ 1` | `‖C_n i j‖ ≤ 1` |
| `reported_bounds`, `phase_drive_bounds`, `phase_normalized_drive_bounds`, `phase_positiveRow_bound` | `‖C‖ ≤ 1`; `0 ≤ η, μ`, `0 ≤ α ≤ 1`, `‖C0‖ ≤ 1`; `0 < γ` for the normalised/row forms | generic bounds: `0 ≤ reported ≤ 1`, drive in `[−μ, η]`, positive-row envelope `(N−1) η/γ` (survive phase mutants by nature; auditor note N4) |
| `drive_eta_response` | none | `sourceDrive (η+δ) μ C − sourceDrive η μ C = δ · reported C` |
| `main_preM_source_formula`, `main_phase_preM` | none | `preM p (sourceDrive …) B = B + dt ((η+μ) reported − μ − γ B)` on `main`'s `Params` |
| **new** `reported_diag`, `sourceDrive_diag` | none | `reported C i i = 0`, `sourceDrive C i i = −μ` (N2) |
| **new** `reported_offdiag`, `reported_symm`, `sourceDrive_symm` | `i ≠ j` for `_offdiag` | `reported = (‖C i j‖ + ‖C j i‖)/2` and symmetric although `C` need not be (N1) |
| **new** `main_phase_stepM_eq_stepB` | `B` symmetric, `Fintype V`, `LinearOrder V` | link to `MatrixForm.stepM_eq_stepB` for the phase drive |
| probes (`probe_coherence_values`, `probe_reported_second`, `probe_drive_second`, `probe_main_preM`, …) | none | node-uniform probe, `D = 2`, `x0 = 0`, `u = π/2`, `ω = 1`, `τ = π`, `α = 1/2`, `C0 = 1` (as deposited) |
| **new** `probe_asym_coherence_values`, `probe_asym_directed_magnitudes`, `probe_asym_directed_ne` | none | (N1, N5) `D = 1`, `x0 = 0`, `ω = 0`, `τ = 0`, node 0 advances `π/2` per step, node 1 not, `α = 1/2`, **`C0 = 0` (engine zero init)**: `C₂ 0 j = 1/4 + i/2`, `C₂ 1 j = 3/4`; `‖C₂ 0 1‖ = √5/4 ≠ 3/4 = ‖C₂ 1 0‖` |
| **new** `probe_asym_reported`, `_swapped`, `probe_asym_drive`, `probe_asym_reported_diag` | none | reported `= (3 + √5)/8` in both directions (proved by unfolding `reported`, **not** through `reported_offdiag`), drive `= 3 (3+√5)/8 − 1` at `η = 2, μ = 1`; diagonal `0` |
| **new** `probe_alpha_quarter` | none | `α = 1/2` is self-dual so the older probes cannot see an `α ↔ 1−α` swap; with `α = 1/4`, `C₁ = 3/4` |
| **new (audit fix)** `Phase.probe_delayed_increment_values`, `Phase.probe_input_delay_values`, `probe_input_offset_value` | none | closed-form value probes of the definitions (`delayedIncrement 2` of `u n = n+1` is `0, 0, 1, 2`; `D = 1` input `z₁ 0 0 = i`; input at read time 0 with `ω = 1, τ = π` is `−1`); the only credit-bearing pins of M37–M39 and M43 |

**Fix list from the audit.** (a) the asymmetric node-dependent probe above pins the symmetrised average (the "reported = `‖C i j‖` only" mutant is now
killed, M51); (b) `reported_diag` and the direct `probe_asym_reported_diag` pin the zero diagonal (M52); (c) the `wrong_*_refuted` lemmas are renamed
`inputPhasor_delay_{three,one,zero}_differs`, `inputPhasor_no_offset_differs`, `constant_input_differs`, `drive_without_eta_differs` and their
docstring says they are facts about the function `Phase.inputPhasor` (and two arithmetic comparisons), not mutation evidence; the mutation evidence is
the check in `lean_mutation_check.py` (§11.3); (d) the C0 = 0 probe (zero initial coherence, as the engine's `coherence_acc`).

**Transcription is hand-checked, not proved against Python.** `coherenceInput` is read off `aief_experiment_engine_v1.py` `compute_R` (about
lines 735-751: `dphi = theta_i − delayed_j − mean(omega) tau`, EMA `alpha C + (1 − alpha) z`, `abs`, `0.5 (R + R^T)`, zero diagonal; the engine
initialises `coherence_acc` to zeros) and `reported`/`sourceDrive` off the `advance_state` drive (about lines 790-794: `B + dt ((eta+mu) R − mu − gamma B)`);
Auditor Seat 002 and Researcher 001 each compared these lines by hand. `test_lean_gate_p5.py` additionally checks the Lean values against an independent
floating-point simulation of the same convention (also hand-written from the same lines). No theorem relates this Lean model to the Python code.

**Scope (not covered).** The trajectory of `B` itself, phase locking, the clip/projection (`np.maximum`, symmetrisation of `B`) and `shuffle_driver` (the
driver `R` used in `advance_state` may be shuffled); float64 and the `fmod`/remainder of the Python phase wrap (`wrapPhase` is the exact-real floor wrap);
`D = 0` and `τ`, `ω` arbitrary reals are covered by the general statements but only `D ∈ {1, 2}` is probed.

### 11.2 Numbering of the mutants

`MUTANTS` holds the statement mutants: M1–M23 (P1–P4a) and M24–M36 (P4b, on `main` since PR #26); the #27 follow-ups add M57–M58 (§11.7). The P5 mutants are
definition mutants (a second kind, see below), numbered **M37–M52** as ported plus **M53–M56** added for the auditor's note N2 (§11.7), and live in a separate list
`DEF_MUTANTS` (20 entries, M37–M56). Exact pin: `test_lean_gate_p5.py` (`TOTAL_MUTANTS` = 38 statement + 20 definition = **58**; the P4b test pins `len(MUTANTS) == 38`;
before the 2026-11-11 refresh the pin was 23 + 16 = 39 on the branch and 36 + 16 = 52 expected after P4b, 52 + 4 definition + 2 statement mutants = 58 now).

### 11.3 Mutation check: M37–M52 (16 definition mutants)

*(Written before the 2026-11-11 refresh; the counts in this section and in §11.4 (16 definition, 39 in total, 9 equivalence controls, one documented survivor) are superseded by §11.7: 20 definition mutants M37–M56, 38 statement mutants, 58 in total, 10 equivalence controls, no survivor.)*

Why a new kind. M1–M36 change a theorem *statement* and are refuted by a proved negation theorem. The survivors reported for cycle 004 and cycle 013 are wrong
*implementations* (a different delay index, a swapped `i j`, a one-sided `reported`, …): a mutated definition has no statement to refute, so steps (b)/(c) of
the original rule cannot apply.

**Rule change after the audit of `64f39eb` (written reason).** The first version of the definition-mutant rule was: the mutated file fails to build with a "REAL PROOF
FAILURE" and one of the pin *theorems* fails. Auditor Seat 002 showed it scores semantically **equivalent** rewrites as killed (`inputPhasor … * 1`, `(… + 0)`, `id (…)`
in `coherenceInput`: `input_engine_convention` fails with unsolved goals) and even a **misspelled identifier** (one "Unknown identifier" plus cascading unsolved goals
classified as real). So 16/16 measured the brittleness of rewrite lemmas, not detection. The rule is now stricter (nothing is relaxed): a definition mutant is **KILLED
iff** (1) the mutated file fails to build; (2) **no error line anywhere is a name-reference error (Unknown identifier/constant/namespace) or a parse error** (otherwise the
mutant is INVALID, which fails the run); (3) at least one of the **value probes** declared for that mutant fails. Value probes (`VALUE_PROBES`) are the closed-form
equalities `f (concrete data) = concrete value` proved from the definitions (`probe_*`); rewrite lemmas (`input_engine_convention`, `delayed_input_step`,
`innovation_*`, `reported_symm`, `reported_diag`, …) give **no credit**, because they fail under equivalent rewrites too. New value probes added for this:
`probe_delayed_increment_values` (`delayedIncrement 2` of `u n = n+1`: `0, 0, 1, 2`), `probe_input_delay_values` (D = 1, node 0 advancing `π/2`: `z₁ 0 0 = i`, newest slot
would give `1`; proved from the definitions, not through `delayed_input_step`) in `PhaseIncrement.lean`, and `probe_input_offset_value` (`ω = 1, τ = π`: input at read time 0
is `−1`, proved by `simp` from the definitions) in `PhaseCoherence.lean`.

**What "KILLED" means (auditor note N1, added in the 2026-11-11 refresh).** For a *definition* mutant, KILLED means exactly this: the mutated file fails to build, no error
line is a name-reference or parse error, and **a declared closed-number value probe fails to build** (the probe is a theorem `f (concrete data) = concrete number` whose proof no
longer elaborates). It does **not** mean that the mutant "computes a different value": the harness never evaluates the mutated definition and never compares two values; it only observes
which probe declarations stop elaborating. A probe can in principle also fail for a reason other than a changed value (a brittle proof script); the equivalence controls below bound that.

**Negative controls (the run FAILS if any is not as expected):**

* *Equivalence controls* (10 since the refresh, 9 before; must NOT be killed, i.e. no declared value probe of the file fails): E1 `* 1`, E2 `+ 0`, E3 `id (…)` on `coherenceInput`; E4 `¬ n < d` for `d ≤ n`,
  E5 `u (n − d + 0)` and E6 another proof term for the oldest slot on the 011 delayed read / input read; E7 reordered EMA sum; E8 commuted `‖C i j‖ + ‖C j i‖` in `reported`;
  E9 `(μ + η)` for `(η + μ)` in the drive, E10 `(ω_j + ω_i)/2` for `(ω_i + ω_j)/2` in the static offset of `inputPhasor` (added with N2; its first version of the probe was killed
  by E10 and by E1/E2 on the new coherence probe, see §11.7). (A first version of `probe_input_offset_value` closed its goal with `exact reference_zero …` and was killed by E1/E2, i.e. it
  was itself brittle; it was re-proved by `simp` from the definitions, after which E1/E2 are not killed. This was caught by the controls, which is their purpose.)
* *Typo controls* (3; must be classified INVALID and not killed): T1 `inputPhasorXX`, T2 an unbalanced parenthesis (parse error), T3 `delayedIncrementXX`.
* *Statement-level controls* (2, on M4's statement): SE1 an equivalent rewrite `(1 − dt·γ)` and ST1 a typo `branchScaleXX` must NOT be rejected.
* Known survivor S1 was documented here before the refresh; since N2 it is the counted mutant M55 and `KNOWN_SURVIVORS` is empty (§11.7). Mutants in `KNOWN_SURVIVORS` would be run and reported but not counted; a survivor that starts being detected fails the run (stale list).

**Re-check of the 23 statement mutants (M1–M23).** They are protected by step (b), which the definition mutants lacked: the mutated statement must be refuted by a *proved
negation theorem* (standard axioms, no `sorry`), and an equivalent statement is true so no negation applies, while a misspelled statement does not elaborate in the refutation
file at all. The two statement-level controls above test exactly that. Their build step (a) keeps the P3 classifier (name-reference-only failures give no credit, mixed
ones do); the run now **flags** any statement mutant whose build output also contains a name-reference/parse error line (information only; result below). The classifier itself
is not changed: M1–M23 were designed so that the kept proof fails on the type, and tightening it would change P3's recorded rule without a demonstrated weakness (the
verdict of every statement mutant also needs (b) and (c)).

| # | Mutant (definition changed, proofs kept) | File | Value probe(s) declared and observed failing |
|---|---|---|---|
| M37 | `delayedIncrement`: `d ≤ n` → `d < n` (011 auditor mutant) | PhaseIncrement | `probe_delayed_increment_values` |
| M38 | `delayedIncrement`: `u (n−d)` → `u (n−d+1)` | PhaseIncrement | `probe_delayed_increment_values` |
| M39 | `inputPhasor` reads the newest slot instead of the oldest | PhaseIncrement | `probe_input_delay_values` |
| M40 | 004: wrong delay index, `D` → `D+1` | PhaseCoherence | `probe_coherence_values`, `probe_asym_coherence_values` |
| M41 | 004: wrong delay index, `D` → `D−1` (younger read) | PhaseCoherence | same |
| M42 | 004: current `θ` instead of the delayed `θ` | PhaseCoherence | same |
| M43 | 004: dropped `ω·τ` offset (ω := 0) | PhaseCoherence | `probe_input_offset_value`, `probe_coherence_values` (both fail) |
| M44 | 004: `phase := 0` (input `1`) | PhaseCoherence | `probe_coherence_values`, `probe_asym_coherence_values` (and `probe_input_offset_value`) |
| M45 | 004: missing `η` (`(η+μ) R` → `μ R`) | PhaseCoherence | `probe_drive_second`, `probe_asym_drive` |
| M46 | 013 (auditor): swap `i`/`j` in `coherenceInput` | PhaseCoherence | `probe_coherence_values`, `probe_asym_coherence_values` |
| M47 | 013 (auditor): conjugated input | PhaseCoherence | same |
| M48 | 013 (auditor): `α` ↔ `1−α` in the EMA | PhaseCoherence | `probe_alpha_quarter` only (the `α = 1/2` probes are blind to it) |
| M49 | 013 (auditor): drive `−μ` → `+μ` | PhaseCoherence | `probe_drive_second`, `probe_asym_drive` |
| M50 | 013 (auditor): trace step uses the input of step `n+1` (off by one) | PhaseCoherence | `probe_coherence_values`, `probe_asym_coherence_values` |
| M51 | 013 survivor: `reported` one-sided (`‖C i j‖` only) | PhaseCoherence | `probe_asym_reported` (also `probe_asym_reported_swapped`) |
| M52 | 013 survivor: `reported` diagonal `1` instead of `0` | PhaseCoherence | `probe_asym_reported_diag` |
| M53 | (N2) `inputPhasor` offset `(ω_i+ω_j)/2·τ` → `ω_i·τ` (wrong index / node-uniform `ω_i`) | PhaseIncrement | `probe_input_asym_omega_value` |
| M54 | (N2) offset → `ω_j·τ` (wrong index) | PhaseIncrement | `probe_input_asym_omega_value` |
| M55 | (N2) offset dropped (formerly the documented survivor S1) | PhaseIncrement | `probe_input_asym_omega_value` |
| M56 | (N2) `coherenceInput` reads a node-uniform `ω` (`fun _ => ω i`) | PhaseCoherence | `probe_coherence_input_asym_omega` |

Former known survivor **S1** (documented before the 2026-11-11 refresh, now the counted M55): dropping the static offset `(ω_i+ω_j)/2·τ` in `PhaseIncrement.inputPhasor` alone is not detected by that file's theorems or value probes
(the offset cancels in the step ratio; Auditor Seat 002's note on 011; no value probe of that file involves `ω` or `τ`). It **is** killed one level up by the value probes
`probe_input_offset_value` and `probe_coherence_values` of `PhaseCoherence.lean` (M43), so "pinned one level up" now rests on value probes, not on `input_engine_convention`.

Result as recorded before the refresh (local, 2026-11-10; full run of the revised rule, `lean_mutation_check.py`): positive controls PASS (8 files), both validator negative controls REJECTED, classifier negative
control PASS; **23/23 statement mutants rejected (M1–M23 unchanged; 0 of them flagged with a name-reference/parse error line)**; statement controls SE1 (equivalent) and ST1 (typo)
NOT rejected; **16/16 definition mutants KILLED by a declared value probe (M37–M52), 39/39 in total; no counted survivor**; **9/9 equivalence controls NOT killed** (E1–E5, E7–E9 fail
only in rewrite lemmas, E6 builds); **3/3 typo controls flagged INVALID** (unknown identifier, parse error, unknown identifier); S1 survives as documented. RESULT PASS.
Under the first version of the rule E1, E2 and E3 would have been scored killed and T1 too (audit of `64f39eb`). The value probes that actually failed are in the table above
(per mutant); rewrite lemmas also failed for most mutants but earn no credit. No mutant, pin or proof was changed after seeing a mutation result, except the re-proof of
`probe_input_offset_value` described under the controls (it was itself brittle: killed by E1/E2) and the pin changes recorded earlier (M48 → `probe_alpha_quarter`, M51/M52 → direct
probes). Limits that remain: a value probe can still fail because its *proof script* is brittle rather than because the value differs; the equivalence controls bound this (nine
rewrites, none kills) but cannot exclude it for other rewrites. The `ω` probes used a node-uniform `ω`, so a mutant replacing `(ω_i+ω_j)/2` by `ω_i` was not in the list; that gap is closed by N2 (M53–M56, §11.7).

### 11.4 Gate results before the refresh (local, 2026-11-10, Europe/Tirane; the refreshed numbers are in §11.7)

* `SKIP_CACHE=1 ./check_lean_gate.sh`: PASS, 2297 jobs, 0 warnings, 18 `.lean` files (root + 17 modules; 3 modules new) hashed in `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` (22 entries),
  step 6: 18 files scanned, 0 hits, **615 declarations audited** (512 on `main`; +103 for the three new files, 3 of them the audit-fix value probes), every one depending only on
  `propext`, `Classical.choice`, `Quot.sound` (`disallowed=0`). Iterations: two for the first commit (Mathlib line-length linter; a docstring line starting with `theorem` read by the step-7
  declaration scan), none for the audit-fix commit; no proof changed.
* `lean_mutation_check.py` (full run): 39/39 with the revised rule plus 9 + 3 + 2 controls (above).
* `research/lean_gate/tests`: 52 passed (40 before P5; `test_lean_gate_p5.py` has 12 tests: restated statements vs the deposit, banned markers and credit by handle, fix lemmas present,
  the probes against an independent simulation, the exact counts 23 + 16 = 39 mutants and 9 / 3 / 2 controls, every edit applies once and every pin is a value probe, the revised kill rule's
  negative controls incl. name-reference and parse errors anywhere, closed-value-equality shape of the probes).
* Repository checks (`tools/ci`, local venv): `check_artifact_pins`, `check_sha256sums`, `check_modes --strict`, `hygiene_scan --pii`, `lint_claims`, `check_manifest`, `check_current_inventory`,
  `check_pinned_restatement` all PASS; `unittest discover tools/ci/tests`: 179 tests OK. `registry/artifacts_current.csv` regenerated after staging (the builder lists tracked files only).
* Not done at that time (not on `main`): mutants for the auditor's `Capacity` lemmas `preM_between` and `convex_weights_iff` (PR #27); added as M57–M58 in the refresh (§11.7). `Capacity.lean`, `.github/` and `Pinned/` are untouched.

### 11.5 Expected merge conflicts with P4b (PR #26) (as predicted before the merge; what actually happened is in §11.7)

Both branches append to the same places: `AIEFGateCore.lean` (import lines), `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` (regenerate), `README.md` (table/summary text),
this SPEC (§10 vs §11 appended at the end), `research/lean_gate/lean_mutation_check.py` (P4b appends M24–M36 to `MUTANTS` and edits `OPENS`/docstring; P5 adds `DEF_MUTANTS`,
`KNOWN_SURVIVORS` and helpers after `MUTANTS` and a loop at the end of `main`), `registry/artifacts_current.csv` (regenerate with
`build_current_inventory.py`) and `tests/test_lean_gate_p4a.py` (P4b relaxes `== 23` to `>= 23`; P5 does not touch it). No Lean file is shared (P4b: `WeightUpdate.lean`, `Freeze.lean`;
P5: `HistoryBuffer.lean`, `PhaseIncrement.lean`, `PhaseCoherence.lean`). The declaration count after both merges is not the sum of the two gate totals as printed here
(P4b 599, P5 612, base 512): expect `512 + 87 + 100 = 699` (to be re-measured).

### 11.6 Still open (P5)

* No proof that the Lean convention is the Python one (hand-checked only); `shuffle_driver`, the clip/projection and the `B` trajectory are outside the model.
* Probes use `D ∈ {1, 2}`, `Fin 2` and phase multiples of `π/2`; the general statements cover all `D`, `V`, `ω`, `τ`.
* The generic bounds (unit disk, drive range, row envelope) survive phase mutants by nature (auditor note N4); they are not evidence about phases.
* `α = 1/2` probes cannot see an `α ↔ 1−α` swap; `probe_alpha_quarter` and `innovation_engine_convention` do.
* No Lean-side statement pin (Lea-style statement hash) in CI; the mutation check runs in CI since PR #27 (`.github/workflows/lean.yml`, step "Lean-gate mutation check (AIEFGateCore only)"; PR #28 pins that step with a guard test). The Lean-side statement pin is still open.
* **AUD-RATELAW stays UNEXPLAINED.**

### 11.7 Merge refresh onto `main` and auditor notes N1/N2 (2026-11-11, Europe/Tirane)

**Merge.** `research/lean-gate-p5` (tip `54037ea`) was merged (merge commit, no rebase, no force-push) with `origin/main` (`1c30ca5`: P4b = PR #26 and the #27 follow-ups; later `main`
commits are merged in a second merge commit, see the commit log). Six files conflicted (12 hunks), resolved as follows: `AIEFGateCore.lean` keeps `Freeze`, `WeightUpdate` and the three P5
imports; `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` regenerated with the command in `check_lean_gate.sh` (24 entries); `lean/AIEFGateCore/README.md` (3 hunks) lists P4a, P4b and P5 in
the summary, both table rows, and both mutant sentences (M14–M23 P4a, M24–M36 P4b, M37–M56 P5 definition mutants); `registry/artifacts_current.csv` kept both sides then rebuilt with
`build_current_inventory.py` after `git add`; this SPEC keeps §10 (P4b) then §11 (P5); `lean_mutation_check.py` keeps M24–M36 in `MUTANTS`, `DEF_MUTANTS`, `def_mutant_status`, the
equivalence/typo/statement controls and `AIEF_MUT_ONLY` (now also honoured by the definition-mutant loop). No pinned file is touched.

**N1 (wording).** §11.3 now states that KILLED for a definition mutant means a declared closed-number value probe fails to build, not that the mutant computes a different value; the
docstring of `lean_mutation_check.py` says the same.

**N2 (asymmetric `ω`).** Every earlier probe had a node-uniform `ω` (`1` or `0`), so `(ω_i+ω_j)/2` could be replaced by `ω_i` or `ω_j` unseen, and dropping the offset in `PhaseIncrement.lean`
alone survived (S1). New value probes: `PhaseIncrement.probe_input_asym_omega_value` (`ω = (1, 0)`, `τ = π`, `D = 1`, no increments, read time `0`: the four inputs are `−1, −i, −i, 1`
for `(0,0),(0,1),(1,0),(1,1)`) and `PhaseCoherence.probe_coherence_input_asym_omega` (the same on `coherenceInput`). New definition mutants (probes declared in `DEF_MUTANTS`): M53 `ω_i·τ`,
M54 `ω_j·τ`, M55 offset dropped (the former S1), all on `PhaseIncrement.lean` line 58 and killed by `probe_input_asym_omega_value`; M56 `fun _ => ω i` in `coherenceInput`, killed by
`probe_coherence_input_asym_omega`. Consequence: S1 is now detected, so `KNOWN_SURVIVORS` is empty (a stale entry would fail the run) and the survivor test was changed accordingly. A new
equivalence control E10 (commuted offset sum) guards the new probe. The first versions of the probes were brittle: the control run caught E1/E2 killing the coherence probe (`exact` on
the unchanged shape) and E10 killing the `PhaseIncrement` probe (rewrite with a fixed summand order); both were re-proved with `simp`/closed numerals (no `add_comm`, which the unmutated
build reports as an unused simp argument), after which no control is killed.

**#27 mutants (optional, added).** M57: `Capacity.preM_between` with `h1 : γ dt ≤ 1` weakened to `True`, refuted by `Capacity.false_preM_between_no_bound`; M58: `Capacity.convex_weights_iff`
with the upper bound dropped from the right side, refuted at `γ = 1`, `dt = 2` (the left side then fails while the weakened right side holds). Numbered after M56, so nothing collides
(M37–M56 definition mutants, M57–M58 statement mutants appended to `MUTANTS`). `OPENS` gained `open AIEFGate.MatrixForm (preM)`; the P4b shape test now pins `len(MUTANTS) == 38`.

**Results (local, 2026-11-11).** `SKIP_CACHE=1 ./check_lean_gate.sh`: PASS, 2299 jobs, 0 warnings, 20 `.lean` files hashed (24 entries), step 6 0 hits, **707 declarations audited**
(`propext`, `Classical.choice`, `Quot.sound` only). Full `lean_mutation_check.py`: unmutated controls PASS, validator and classifier negative controls PASS; **38/38 statement mutants rejected**
(one flagged with a name-reference/parse line, information only: M31); statement controls SE1/ST1 not rejected; **20/20 definition mutants KILLED by a declared value probe (M37–M56), 58/58 in
total**; **10/10 equivalence controls not killed**; **3/3 typo controls INVALID**; RESULT PASS. Controls of the earlier numbers (23 + 16 = 39, 9 controls) are superseded by 38 + 20 = 58 and 10.

## 12. C014 (branch `research/lean-gate-c014`, tip `9b9b3d9`; merge-refreshed on 2026-11-14 onto `main` `7129d31`)

### 12.1 What it is

`lean/AIEFGateCore/AIEFGateCore/TrajectoryInvariants.lean` (namespace `AIEFGate.TrajectorySafety`) ports cycle 014 of
Researcher 040282 (deposit md5 `c6914623bfcc3002cb1ab0a47e848698`). For any drive `F` and auxiliary update `U`, every
`stepM` weight state after time 0 is structural (needs only `0 ≤ cap`, `0 ≤ ε` of that step) and, under `EngineGate`
of that step's parameters, is row-capped, entry-enveloped, and gives bounded sine coupling and phase increment. These
are induction wrappers around the P4a one-step facts in `Capacity.lean`; no new one-step mathematics. The full-reset
witnesses (`pWide`) say nothing about the engine's parameters. The Auditor review the header cites
(`2026-11-10_audit_040282_c014.md`) is not in this repository.

### 12.2 Mutants (numbered from M71; the c016 port, §13, comes after these: its definition mutants are M79–M86)

| Mutant | Kind | Edit | Killed by |
|---|---|---|---|
| M71 | statement | `post_capacity`: cap of step `n` -> cap of step `n+1` | `capacity_clock_refuted` |
| M72 | statement | `all_times_structural`: initial-structure hypothesis -> `True` | `initial_time_refuted` |
| M73 | statement | `post_capacity`: `EngineGate` hypothesis -> `True` | `broken_link_refuted` |
| M74 | definition | `weightUpdate := symM` (gate bypassed) | probe `probe_gate_scales_row` (`3/4`; bypass gives `3`); also breaks `weightUpdate_structural`, `post_capacity`, `wide_resets_zero`, `wide_resets_one`, `broken_link_refuted` |
| M75 | definition | `feedbackStep` gives `U` the old `B` twice (Researcher 001's survivor on `9b9b3d9`) | probe `probe_aux_reads_old_and_new` (`-1`; gives `-11`) |
| M76 | definition | `feedbackStep` gives `U` the new `B` twice | probe `probe_aux_reads_old_and_new` (gives `0`) |
| M77 | definition | `feedbackStep` gives `U` the raw drive `F n state.1 state.2` instead of the new `B` (Researcher 001's survivor on `3a4c75b`) | probe `probe_aux_time_and_new_entry` (`15/2`; gives `30`) |
| M78 | definition | `feedbackStep` gives `U` the time `n + 1` (Researcher 001's survivor on `3a4c75b`) | probe `probe_aux_time_and_new_entry` (gives `17/2`) |
| E11 | equivalence control | the `let Bnew` of `feedbackStep` inlined | must NOT be killed |

The three value probes are new (not in the deposit) and sit in a marked block of the module. `OPENS` gained
`open AIEFGate.TrajectorySafety (Weights weightsTrace Structural)`; statement mutants use the closure `TS_VARS`.

### 12.3 Tests

`research/lean_gate/tests/test_lean_gate_c014.py` pins the module import and hash, no escape hatches, `#print axioms`
for the probes, the shape of M71–M78 and E11 (selected by file, not list position), that each edit applies, that mutant and
control numbers stay unique, and recomputes the three probe values (and the mutant values) in exact rationals from `preM`/`clipM`/`symM`/`scale`/`GateOnX`/
`kernelM` (text-pinned). The P4b and P5 tests' count pins were moved to 41 statement / 25 definition / 66 total and
11 equivalence controls, with the P5 checks selecting P5 entries by file.

### 12.4 Results (local, 2026-11-14)

`SKIP_CACHE=1 ./check_lean_gate.sh`: PASS, 2300 jobs, 0 warnings, 25 files hashed, step 6 0 hits, **789 declarations
audited** (`propext`, `Classical.choice`, `Quot.sound` only). Full `lean_mutation_check.py`: **41/41 statement and
23/23 definition mutants killed, 64/64**; 11/11 equivalence controls not killed; 3/3 typo controls INVALID; RESULT PASS.

Follow-up (Researcher 001's notes on `3a4c75b`): with `probe_aux_time_and_new_entry` and M77/M78 added, the gate PASSes with
**794 declarations** and the full mutation run gives **41/41 statement, 25/25 definition, 66/66**; 11/11 equivalence
controls not killed; 3/3 typo controls INVALID; RESULT PASS.

### 12.5 Still open (C014)

* `U` and `F` are arbitrary, so nothing here says the engine's feedback is safe beyond the one-step gate facts.
* No Python-side check that the engine passes old and new `B` in this order (the probe only pins the Lean convention).
* The oscillation witnesses use a full-reset `pWide` step; they are not evidence about engine parameters.

## 13. P6 (branch `research/lean-gate-c016`, from `main` `7129d31`, which contains P5 (#31), the guard fixes (#32, #36), the engine step-order work (#33), the E22 docs (#34) and the claims fix (#35); merge-refreshed on 2026-11-14 onto `main` `871417d`, which also contains C014 (#37, §12) and its follow-up (#38))

Port of Researcher 040282's cycle 016 (`CoherenceMotion`) into `lean/AIEFGateCore/AIEFGateCore/CoherenceMotion.lean` (namespace `AIEFGate.CoherenceMotion`, imported by `AIEFGateCore.lean`),
with the notes of Auditor Seat 002's review (`audit_inbox/2026-11-11_auditor-seat-002_lean-candidate-reviews/2026-11-11_audit_040282_c012_c016.md`, verdict **ADOPT WITH NOTES**). Nothing under
`Pinned/`, `lean/AIEFProofs*`, `lean/AIEFFreezeCore`, `Capacity.lean`, `.github/` or any other hash-pinned artifact is edited. **AUD-RATELAW stays UNEXPLAINED**; this package
does not touch it.

**Credit.** Statements and proofs come from Researcher 040282 (handle only). Cycle 016: `CoherenceMotion.lean`, md5 `079a72f37e16e2187a913b96e28ab605`; the file is owner-supplied (the owner supplied it), and
a copy is on branch `audit-inbox` at `audit_inbox/2026-11-08_researcher-040282/researcher_040282/cycle_016/CoherenceMotion.lean` (the md5 of that copy was checked; it is read-only
evidence and is not imported). The deposit imported the then-unmerged P5 branch at `54037ea`; this port imports the merged `AIEFGateCore.PhaseCoherence`. The merged names are the
names the deposit used (`PhaseCoherence.reported`, `coherenceStep`, `coherenceTrace`, `coherenceInput`, `input_norm`, `input_engine_convention`, `coherenceTrace_unitDisk`,
`reported_bounds`, `reported_diag`, `reported_offdiag`, `Phase.phaseTrace`, `Phase.wrapPhase`), so no import or identifier had to be retargeted (review note N3).
`test_lean_gate_c016.py` records the whitespace-removed deposit statements (21 theorems) and checks that the restated statements agree. No deposited Python was executed.

**What it says, and what it does NOT say.** For the coherence EMA `C_{n+1} = α C_n + (1 − α) z_{n+1}` with unit-modulus input `z` and `0 ≤ α ≤ 1`, the reported coherence
`R = reported C` satisfies `α R − (1 − α) ≤ R' ≤ α R + (1 − α)` and `|R' − R| ≤ (1 − α)(1 + R)`. With every entry of `C0` in the unit disk, `|R_{n+1} − R_n| ≤ min 1 (2 (1 − α))`
and the diagonal of `R` is `0`. At the engine `α = exp(−dt/T_window) = 0.99942883…` (`dt = 1/100`, `T_window = 25 / mean ω`, `mean ω = 857/600` (`FROZEN_DT`, `FROZEN_OMEGA`,
`FROZEN_T_WINDOW`, `FROZEN_ALPHA` of `aief_experiment_engine_v1.py`), so `α = exp(−857/1500000)`), `2 (1 − α) = 0.0011423…`. What the theorems prove is the per-step bound. A step count from it alone is a weak lower bound: a change of `R` of size `1` takes at least `1/(2(1−α)) = 875.4`, i.e. `876`, steps, and `2 (1 − α)` is attained within one step only (`engine_factor_two_attained`), not sustained. The envelopes iterate to more (audit of `d551540`, note N2): `R' ≤ αR + (1−α)` gives `1 − R_n ≥ α^n (1 − R_0)` (`trace_rise_bound`) and `R' ≥ αR − (1−α)` gives `1 + R_n ≥ α^n (1 + R_0)` (`trace_fall_bound`). At the engine `α`, `α^1213 > 1/2 > α^1214` (`ln 2 / (857/1500000) = 1213.2`): from `R_0 = 0` the reported coherence is still below `1/2` after `1213` steps, so it needs at least `1214` steps to reach `1/2` (`engine_rise_half_not_before_1214`; for `R_0 < 1`, `α > 0` it is below `1` at every finite step), and from `R_0 = 1` it is still above `0` after `1213` steps (`engine_fall_zero_not_before_1214`). It needs at least `4031` steps to go from `0` to `0.9` (`ln 10 / (857/1500000) = 4030.2`, exact arithmetic, checked in `test_lean_gate_c016.py`, not by a Lean theorem). The `1214` figures are for these start values and thresholds only (attained under constant input `−1`, so they are tight there). **This is a triangle-inequality speed limit on an exponential moving average with unit-norm inputs. It uses no phase structure, no delay, no `ω` and no `B`:
the same bound holds for ANY unit input sequence. It does not say that `R` converges, locks or stays near a value, and it says nothing about `B`, the clip/projection or the gate.**
(The only fact about the phase machinery that is used is that the input has modulus one, `PhaseCoherence.input_norm`, directly or through `coherenceTrace_unitDisk` and `reported_bounds`.)

### 13.1 What is proved (all on `CoherenceMotion.lean`; exact reals; `V` any type)

| Theorem | Hypotheses (exactly as proved) | Content |
|---|---|---|
| `complex_step_bounds` | `0 ≤ α ≤ 1`, `‖z‖ = 1` | `α‖C‖ − (1−α) ≤ ‖αC + (1−α)z‖ ≤ α‖C‖ + (1−α)` |
| `reported_nonneg` | none | `0 ≤ reported C i j` |
| `reported_step_bounds`, `reported_step_signed`, `reported_step_abs_state_bound` | `0 ≤ α ≤ 1` | one-step envelope of `reported` for the real `coherenceStep` (no unit-disk premise): `αR−(1−α) ≤ R' ≤ αR+(1−α)`; `−(1−α)(1+R) ≤ R'−R ≤ (1−α)(1−R)`; `|R'−R| ≤ (1−α)(1+R)` |
| `rTrace` (def) | – | observable wrapper `reported (coherenceTrace α C0 d x0 u ω τ n) i j`; no new state or recurrence |
| `trace_step_bounds`, `trace_step_abs_state_bound` | `0 ≤ α ≤ 1` | the same on the trace |
| `trace_step_abs_le`, `trace_step_abs_le_min` | `0 ≤ α ≤ 1`, `‖C0 i j‖ ≤ 1` | `|R_{n+1} − R_n| ≤ 2(1−α)` and `≤ min 1 (2(1−α))` (the unit disk is inherited from `C0` through `coherenceTrace_unitDisk`) |
| `trace_diagonal` | none | `rTrace … n i i = 0` |
| probes `probe_half_drop`, `probe_half_increase`, `probe_two_step`, `factor_two_attained`, `increase_factor_attained` | none / `1/2 ≤ α ≤ 1` / `α ≤ 1` | node-uniform data: `D = 1`, `x0 = 0`, `u = 0`, `ω = 1`, `τ = π` (input `−1` everywhere), constant `C0 = c`: `α = 1/2`, `c = 1`: `R = 1, 0`; `c = 0`: `R = 0, 1/2`; `α = 3/4`, `c = 1`: `R_2 = 1/8`; the factor `2` is attained for `α ≥ 1/2` (not a claim of optimality for other `α` or zero-initialised trajectories) |
| refutations `factor_one_refuted`, `increase_only_abs_refuted`, `negative_alpha_upper_refuted`, `alpha_gt_one_upper_refuted`, `nonunit_initial_refuted`, `two_step_one_allowance_refuted` | none | each hypothesis and constant is necessary: factor `1` instead of `2`, an increase-only envelope, `α < 0`, `α > 1`, a non-unit-disk `C0`, and two steps sharing one allowance are refuted by value |
| **new** `probe_diagonal_zero`, `diagonal_one_refuted`, `half_increase_upper_refuted` | none | diagonal `0` at `n = 0, 1` with `C0 = 1`; a diagonal claimed `1` and an upper envelope `(1−α)/2` instead of `(1−α)` are refuted by value |
| **new (N2)** `probe_asym_state` | none | asymmetric state, `C0 0 1 = 1`, every other entry `0`, `α = 1/2`: `R_0 = 1/2`, `R_1 = 1/4`; a one-sided `R` (`‖C 0 1‖` only) would read `1`, `0` |
| **new (N2 of the `d551540` audit)** `trace_rise_bound`, `trace_fall_bound`, `engine_pow_1213_gt_half`, `engine_pow_1214_lt_half`, `engine_rise_half_not_before_1214`, `engine_fall_zero_not_before_1214` | `0 ≤ α ≤ 1` for the two bounds; none for the closed numbers; `R_0 = 0` resp. `R_0 = 1`, `n ≤ 1213` for the last two | `α^n (1 − R_0) ≤ 1 − R_n` and `α^n (1 + R_0) ≤ 1 + R_n`; at the engine `α`: `α^1213 > 1/2 > α^1214` (from `log 2` bounds, `Real.log_two_gt_d9`/`lt_d9`), hence `R_n < 1/2` for every `n ≤ 1213` when `R_0 = 0`, and `R_n > 0` when `R_0 = 1`. Attained under constant input `−1` (`R_n = 1 − α^n` from `C0 = 0`; `R_n = |2α^n − 1|` from `C0 = 1`) |
| **new (engine α)** `alphaE`, `alphaE_exact` (N3 of the `d551540` audit: `alphaE = exp(−(857/1500000))`, pins the mean `ω` numerator), `engine_speed_limit_value`, `engine_factor_two_attained`, `engine_step_value`, `engine_factor_one_refuted` | none | `alphaE = exp(−((1/100)/(25/(857/600))))`: `0.00114 < 2(1−alphaE) < 0.00115` (proved from `1−x ≤ e^{−x}` and `e^{−x}(1+x) ≤ 1`, `x = 857/1500000`); one step of the probe data moves `R` by exactly `2(1−alphaE)`, `0.00114… < |R_1 − R_0| < 0.00115`, and `1−alphaE` does not bound it |

### 13.2 Review notes applied

* **N1 (main limitation: speed limit, not dynamics).** The module docstring and the README row say plainly what the file does NOT say (no phase, delay, `ω` or `B` structure; holds for any unit input sequence; says nothing about convergence, locking, `B`, the clip or the gate). `test_lean_gate_c016.py` checks the wording.
* **N2 (node-uniform probes do not exercise the symmetrisation).** `probe_asym_state` is the new asymmetric-state probe (above). It is the declared pin of the new mutant M71 (one-sided `R`); the node-uniform probes cannot tell the one-sided reading from `reported`
  (`test_lean_gate_c016.py` checks that numerically). For `α < 1/2` the `min` is just `1`, which is trivial because `R ∈ [0,1]`; stated in the docstring.
* **N3 (depends on an unmerged branch).** P5 is merged; the imports were re-checked against the merged names (above) and the file builds against the merged `PhaseCoherence` with the deposit's own import line (`import AIEFGateCore.PhaseCoherence`) and namespaces unchanged; only the deposit's header comment ("UNMERGED team P5 branch 54037ea") was replaced.
* **N4 (float α is not exact).** The bound is about exact reals; the engine `α` is modelled as the exact real `exp(−857/1500000)`, the float64 `FROZEN_ALPHA = 0.9994288298464774` is not that real (stated in the docstring and here).
* **Mutants (review port note).** M60 is the review's suggested mutant, the bound `(1−α)/2` instead of `2(1−α)`; M59 drops the factor `2`.

Audit of `research/lean-gate-c016` at `d551540` (Auditor Seat 002, CLEAN WITH NOTES; numbered here as A1–A4 to keep them apart from the review's N1–N4):

* **A1 (renumbering).** E11 clashed with C014's E11 and M71–M76 with C014's M71–M78; done in the merge with `main` `871417d`, see §13.4 (c016 keeps M59–M70; definition mutants M71–M76 became **M79–M84**, E11–E14 became **E12–E15**; T4 is free, so it stays; this section is §13 because C014 is §12; every `12.x` cross-reference of this section, the README, the module docstring and the tests was updated).
* **A2 (the `875` wording).** Misleading as a step count ("from `0` to `1`" in `d551540`): reworded in the module docstring and in this section (above). The bound `2 (1 − α)` per step gives only `876` steps for a change of size `1`; the audit's suggestion that `875` is "sharp for a fall" is **also not right** (from `R_0 = 1`, `1 + R_n ≥ 2 α^n` forces at least `1214` steps to reach `0`), so no step count is called sharp except the `1214` figures under their stated start values. Added: the closed numbers `engine_pow_1213_gt_half`/`engine_pow_1214_lt_half`, `trace_rise_bound` and `trace_fall_bound` and the corollaries `engine_rise_half_not_before_1214`, `engine_fall_zero_not_before_1214`, and a test with exact arithmetic (`test_rise_is_slower_than_a_fall_audit_n2`). The audit's "about 1213 steps to 1/2" is the real number `1213.2`; the integer is `1214`.
* **A3 (alphaE pin).** `alphaE_exact` (an equality) plus the two closed numbers now pin the mean `ω` numerator; they are declared pins of M82–M86 (`PIN_ALPHA_E`). The near misses are the numbered mutants **M85** (`856/600`) and **M86** (`858/600`, see §13.4): both are killed. **They were also killed by the `d551540` file**: `engine_speed_limit_value` proves its own `alphaE = exp(−(857/1500000))` internally (by `norm_num`) before using the range, so a near-miss `alphaE` already failed *inside that proof*; the audit's remark describes the *statement* (a range), not the proof. The equality is now a declaration of its own, so the pin no longer depends on the proof internals.
* **A4 (scope).** Kept: the docstring says it is a triangle-inequality speed limit and says nothing about convergence or locking.

### 13.3 What changed against the deposit

Statements are unchanged (21 theorem statements, whitespace removed; `1/2 ≤ alpha` is written `1 / 2 ≤ alpha` and long lines are re-wrapped, for the Mathlib whitespace/line-length linters, which are warnings-as-failures here). The deposit's trailing `#print axioms`
lines are removed (step 7 of `check_lean_gate.sh` audits every declaration), and the `set_option linter.style.header false` is dropped (the file has the project header). **The probe proofs were rewritten** (reason below), the file header and docstring were added,
and new items were added (table above). Reason for the proof rewrite: the deposit's probes rewrote with private helper lemmas stated about `rTrace` (`value_r0`, `value_r1`). Compiling the deposit with `rTrace` mutated to read trace `n+1`, only those helpers and the rewrite
lemmas failed and `probe_half_drop`, `probe_half_increase` still built (checked): under the kill rule of §11.3 a probe that still builds earns no credit, so such a mutant would have SURVIVED. The probes now unfold `Rval`/`rTrace`/`reported` themselves
and use only helpers about `coherenceTrace` and `coherenceInput` (untouched by the P6 mutants). The equivalence controls guard against the converse (proof scripts that are brittle under equal rewrites).
**No pass/fail rule of `lean_mutation_check.py` is changed** (kill rule, build-rejection rule and refutation validator are as in §11.3); additions are data: `VP_MOT`, the new entries, and `open AIEFGate.CoherenceMotion (rTrace)` in `OPENS` (the statements of the new mutants mention `rTrace`).
The count pins of `test_lean_gate_p4b.py` and `test_lean_gate_p5.py` were updated (merged totals: 41 + 11 = **52** statement mutants, 25 + 9 = **34** definition mutants, **86** in total; 11 + 4 = 15 equivalence and 3 + 1 = 4 typo controls; the P5 subset M37–M56 and the C014 and P6 subsets are selected by file, not by position); no other assertion was relaxed. New since the first version (audit A2/A3): `trace_rise_bound`, `engine_rise_half_not_before_1214`, `alphaE_exact`, `engine_pow_1213_gt_half`, `engine_pow_1214_lt_half`, and `import Mathlib.Analysis.Complex.ExponentialBounds` (for `Real.log_two_gt_d9`/`log_two_lt_d9`).

### 13.4 Numbering and mutation check: M59–M70, M79–M86 (renumbered after C014; M85, M86 added for audit N3)

`main` `871417d` contains C014 (§12), which owns **M71–M78** (statement M71–M73, definition M74–M78) and **E11**. The c016 mutants were renumbered as agreed with Auditor Seat 002: statement mutants **M59–M69** and definition mutant **M70** keep their numbers; the other definition mutants become **M79–M84**
(old M71→M79, M72→M80, M73→M81, M74→M82, M75→M83, M76→M84); equivalence controls old E11–E14 → **E12–E15**; the typo control **T4** has no clash (C014 has no typo control) and stays. Numbers are unique across ports (`test_c014_numbers_and_no_duplicates` and `test_p6_mutants_exact_counts_and_numbering`).

Statement mutants **M59–M69** (11, refuted by the proved negations of `CoherenceMotion.lean`, same three conditions as M1–M58): M59 `trace_step_abs_le` with factor `2` dropped (`factor_one_refuted`), M60 bound `(1−α)/2` (`factor_one_refuted`),
M61 unit-disk hypothesis `:= True` (`nonunit_initial_refuted`), M62 `R_{n+2} − R_n` with one allowance (`two_step_one_allowance_refuted`), M63 `trace_step_abs_le_min` with `min 1 (1−α)` (`factor_one_refuted`), M64 its unit-disk hypothesis dropped,
M65 `trace_step_abs_state_bound` increase-only `(1−α)(1−R)` (`increase_only_abs_refuted`), M66 `0 ≤ α` dropped from `trace_step_bounds` (`negative_alpha_upper_refuted`), M67 `α ≤ 1` dropped (`alpha_gt_one_upper_refuted`), M68 upper envelope `(1−α)/2`
(`half_increase_upper_refuted`), M69 `trace_diagonal` claiming `1` (`diagonal_one_refuted`). Definition mutants (9, `DEF_MUTANTS`, declared value probes in `VP_MOT`): **M70** `rTrace` reads trace `n+1` (`probe_half_drop`, `probe_half_increase`, `probe_two_step`, `engine_factor_two_attained`),
**M79** `rTrace` one-sided `‖C i j‖` (`probe_asym_state`), **M80** diagonal `1` (`probe_diagonal_zero`), **M81** `rTrace` from one `coherenceStep` of `C0` instead of the trace (`probe_half_drop`, `probe_two_step`, `engine_factor_two_attained`), **M82** `alphaE` with `dt = 1/10`, **M83** `alphaE` with mean `ω = 1`, **M84** `alphaE` with the sign of the exponent
flipped, **M85** / **M86** `alphaE` with the mean `ω` numerator `856` / `858` (audit N3; M82–M86: `PIN_ALPHA_E` = `engine_speed_limit_value`, `alphaE_exact`, `engine_pow_1213_gt_half`, `engine_pow_1214_lt_half`). Equivalence controls **E12–E15**, each of which must not be killed: E12 `rTrace` reads `reported` at `(j, i)` (equal by `reported_symm`), E13 `alphaE = exp(−(857/1500000))`, E14 the symmetrisation written out (`(‖C i j‖ + ‖C j i‖)/2` under `if i = j then 0`), E15 `alphaE` with `T_window = 15000/857`.
Typo control **T4** (`reportedXX`) must be flagged INVALID. The kill rule is unchanged. Totals on `main` + this branch: **52 statement + 34 definition = 86 mutants** (C014: 41 statement = 36 + M57, M58 + 3, 25 definition = 20 + 5; c016: 11 + 9), **15 equivalence controls** (E1–E15), **4 typo controls**, 2 statement controls, `KNOWN_SURVIVORS` empty.

**Near-miss values for the engine `α` (audit N3 of `d551540`): M85, M86.** The first version of this refresh ran `856` and `858` once by hand and added no mutant, because M85 was assumed free for the phase-lock port. They are now counted mutants **M85** and **M86** (`Real.exp (-((1/100) / (25 / (856/600))))`, `858/600`) with the declared pins `PIN_ALPHA_E`; **the phase-lock port (planned M85–M91, E16, §14) must therefore renumber to M87–M93** (E16 is unaffected). Expected and checked: build fails, no name-reference or parse error line, failing declarations among `alphaE_exact`, `alphaE_range`, `engine_speed_limit_value`, `engine_pow_1213_gt_half`, `engine_pow_1214_lt_half` (the closed numbers unfold `alphaE` themselves and do not go through `alphaE_exact`; a first version that did go through it was not mutation-sensitive, because a theorem with an error is still usable downstream, and was changed). For the integers `800…899`, only `857` satisfies `α^1213 > 1/2 > α^1214` (`test_engine_alpha_numerator_is_pinned_exactly_audit_n3`). The unmutated value written another way builds (not killed), as the equivalence controls E13/E15 require.
Two limits, as in §11.3: KILLED means "a pre-declared closed-number probe fails to build", not "the mutant computes a different value" (the numeric difference of each mutant is shown separately in `test_lean_gate_c016.py` with exact rationals); and the symmetric `rTrace` mutant class (E12, E14)
is protected by the controls only.

### 13.5 Gate results (local, 2026-11-15, Europe/Tirane; merge-refresh onto `main` `871417d` with the audit fixes N1–N3)

* `SKIP_CACHE=1 STRICT_ORPHANS=1 lean/AIEFGateCore/check_lean_gate.sh` (`LOG_DIR` outside the repo): **PASS**, 2304 jobs, **0 warnings**, 26 hash entries in `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` (regenerated with the command in the header of `check_lean_gate.sh`), step 6: 22 files scanned, 0 hits, step 7: **843 declarations audited** (794 on `main`; +49 for the new file), every one depending only on `propext`, `Classical.choice`, `Quot.sound`, 0 `sorry`. Iteration: the first build of the N2 additions had 3 over-long lines (linter warnings); re-wrapped, no statement or proof changed afterwards.
* `lean_mutation_check.py`, **full unfiltered run** (no `AIEF_MUT_ONLY`, run on the final Lean sources): unmutated controls PASS, validator and classifier negative controls as before; **52/52 statement mutants rejected** (one flagged with a name-reference/parse error line: the pre-existing M31, information only); **34/34 definition mutants KILLED by a declared value probe** (M82–M86 by `PIN_ALPHA_E`; M85/M86 fail in `alphaE_exact`, `alphaE_range`, `engine_speed_limit_value`, `engine_pow_1213_gt_half`, `engine_pow_1214_lt_half`), **86/86 in total**; **15/15 equivalence controls not killed** (E12 fails only in rewrite lemmas, E13–E15 build); **4/4 typo controls INVALID**; RESULT PASS.
* `python -m pytest research/lean_gate tools/ci/tests`: **310 passed** (124 in `research/lean_gate`, 186 in `tools/ci/tests`); `python -m unittest discover -s tools/ci/tests`: 186 tests OK.
* Repository checks (`/workspace/venv_req_cmp`): `check_artifact_pins`, `check_sha256sums`, `check_modes --strict`, `hygiene_scan --pii`, `lint_claims`, `check_manifest`, `check_current_inventory`, `check_pinned_restatement` all rc 0; `audits/engineering/verify_inventory_current.py` rc 0. `registry/artifacts_current.csv` is rebuilt with `build_current_inventory.py` after `git add`.

### 13.6 Still open (P6)

* Nothing relates the Lean model to float64 or to the Python code beyond the hand-checked convention of §11; the engine `α` is an exact real.
* A speed limit only: no statement about what `R` does, about `B`, about the clip/projection or `shuffle_driver`. The deposit's coupled non-reset/history probe stays deferred.
* The `min` bound is trivial for `α < 1/2`; for `α` near the engine value it is the only quantitative statement about `R` along the real step.
* The probes use `D = 1`, `Fin 2` and zero phases (input `−1`); `probe_asym_state` is the only probe with a non-symmetric state.
* **AUD-RATELAW stays UNEXPLAINED.**
## 14. Frequency lock (branch `research/lean-gate-phaselock`, from `main` `7129d31`, merge-refreshed onto `main` `5788682` and `research/lean-gate-c014-followup` `6a719db`, then on 2026-11-15 onto `main` `ade1179`, which contains P6 (#39, §13); numbered after C014's §12 and P6's §13)

### 14.1 Why

Arena_Researcher_06020041 cycles 3 and 5 (`PhaseLockCoherence.lean` md5 `038cfbeb…`, `LockedCoherence.lean` md5
`6554994d…`, on `audit-inbox` only) compile with standard axioms, but their "lock" hypothesis
`∀ n ≥ N, ∀ i, u n i = 0` is a frozen network. Engine natural frequencies average about 1.43, so it never applies.
Auditor Seat 002 rated them REWORK. `lean/AIEFGateCore/AIEFGateCore/FrequencyLock.lean` is that rework, written by
Auditor Seat 002; no deposited file is copied or executed. This version answers Researcher 001's audit of `02adc22`
(B1, B2, N2-N6).

### 14.2 Statements (all proved; standard axioms only)

The hypothesis is a lock of ONE PAIR `(i, j)`, not of the whole network (B2): from step `N` on, `u n i` and `u n j`
equal the same increment. Nothing is assumed about other nodes; `coherenceInput … i j` reads only `i` and `j`.

* `input_step_of_common_increment`: if `u n i = c n`, `d ≤ n` and `u (n-d) j = c (n-d)`, then
  `coherenceInput (n+1) i j = coherenceInput n i j * phasor (c n − c (n−d))`.
* `coherenceInput_constant_of_periodicPairRate` (B1): with `hlock : ∀ n ≥ N, u n i = c n ∧ u n j = c n` and the
  period condition `hper : ∀ n ≥ N + d, c n = c (n − d)`, `coherenceInput n i j = coherenceInput (N+d) i j` for all
  `n ≥ N + d`. A constant rate is the simplest case, not the only one: `periodic_rate_input_constant` (delay `2`,
  rate `π, 0, π, 0, …`, constant from step `2`).
* `coherenceInput_constant_of_pairLock`: the constant-rate case, `hlock : ∀ n ≥ N, u n i = c ∧ u n j = c`.
* `coherenceTrace_error_of_pairLock`: `C (N+d+k) i j − z = α^k (C (N+d) i j − z)`, `z = coherenceInput (N+d) i j`.
* `coherenceTrace_norm_of_pairLock`: with `0 ≤ α ≤ 1` and `‖C0‖ ≤ 1`, `1 − 2α^k ≤ ‖C (N+d+k) i j‖`.
  (`α ≤ 1` enters through `coherenceTrace_unitDisk`; for `α > 1` the bound is trivially true.)
* `reported_of_pairLock`: for `i ≠ j`, `1 − 2α^k ≤ reported (C (N+d+k)) i j`.
* `pairLock_nonzero_rate` (N3): `unitRate 0 0 ≠ 0` is part of the statement, and the input is constant from
  step 3 at that rate, so the hypothesis is not only the frozen case.
* `common_rate_input_not_constant`, `common_rate_input_ne_zero`: delay 1, both nodes at rate `π, 0, π, …`: the input
  flips sign each step and is nonzero. "The pair moves together" is not enough. `c n = c (n − d)` is sufficient, not necessary: the exact condition is
  `c n ≡ c (n − d)` modulo `2π` (Researcher 001's N1 on `e50102c`: delay 1, rate `2π, 0, 2π, …` keeps the input constant).

Witnesses used by the mutants: `probe_pairLock_one_step` (d = 0, α = 1/2, `C 1 0 1 = 0`, reported `0`),
`pairLock_factor_two_refuted` and `pairLock_norm_factor_two_refuted` (the factor `2` is attained, `1 − α^k` is false),
`half_lock_refuted` (only node `i` locked: input changes), `delay_start_refuted` (constant from `N`, not `N + d`, is
false), `nonperiodic_rate_refuted` (no period condition: false), value probes `probe_unitRate_nonzero`,
`probe_altU_not_constant`, `probe_altU_period_two` and `probe_unitRate_constant`.

How this relates to O1 (`freezing/REPORT.md`, cluster locking; N6): O1 predicts that pairs inside a frequency
cluster lock (`R → 1`) and cross-cluster pairs stay below `R_c`. This section proves only a consequence of the first
half: IF a pair is locked and `α < 1`, its reported coherence tends to `1` (at `α = 1` the bound `1 − 2α^k = −1` says nothing). It does not prove that any engine pair locks and says
nothing about cross-cluster pairs. `reported → 1` means a constant phase difference (phase-locking value `1`), not
equal phases.

### 14.3 Mutants (numbered after P6's M79–M86 and E12–E15; M85–M92 before the 2026-11-15 refresh, shifted by 2)

Statement mutants, each a real build failure plus a refutation by a proved `*_refuted` theorem with standard axioms,
and the same term failing on the unmutated statement:

* M87 `reported_of_pairLock` `1 − 2α^k` → `1 − α^k` (refuted by `pairLock_factor_two_refuted`).
* M88 the same on `coherenceTrace_norm_of_pairLock` (`pairLock_norm_factor_two_refuted`).
* M89 `coherenceInput_constant_of_pairLock` from `N` instead of `N + d` (`delay_start_refuted`, d = 2: `−1` vs `1`).
* M90 `coherenceInput_constant_of_pairLock` with only node `i` locked (`half_lock_refuted`).
* M91 `coherenceInput_constant_of_periodicPairRate` with the period condition dropped (`nonperiodic_rate_refuted`).
* M94 `coherenceInput_constant_of_periodicPairRate` from `N` instead of `N + d` (`delay_start_refuted` at the
  constant rate `π/2`; Researcher 001's N6 on `e50102c`). M89 covers only the constant-rate corollary.

Definition mutants (killed by value probes): M92 `unitRate := 0` (`probe_unitRate_nonzero`), M93 `altU` constant `π`
(`probe_altU_not_constant`). Equivalence control E16 `unitRate := 5` must NOT be killed.

Value probes `VP_FL` (N2 on `e50102c`): the witness theorems themselves cannot be probes (the P5 test requires
value probes to be `probe_*` closed-form facts, so a rewrite lemma can never earn a kill). Instead two value probes pin
the shape they rely on: `probe_altU_period_two` (`altU 2 1 = altU 0 0 ∧ altU 3 1 = altU 1 0`: period `2`, same at
both nodes) and `probe_unitRate_constant` (`unitRate 7 1 = unitRate 0 0`). A definition edit with period 3, a
node-dependent `altU` or a time-dependent `unitRate` now fails a value probe. They are added to `VP_FL`, which makes
the equivalence and typo controls stricter; E16 (`unitRate := 5`) still stays not killed. M92/M93 keep their pins.

Follow-up to Researcher 001's #41 note 1 (`9fd50ba`, 2026-11-17): those probes pin the *shape* of `altU` but not its
*values*, so `altU` with `π/2` in place of `π` passed every probe. A third value probe, `probe_altU_values`
(`altU 0 0 = π ∧ altU 1 0 = 0`), is added to `VP_FL`, and three definition mutants are registered, numbered after
DelayRoots' M95–M106: M107 `altU` with `π/2` (`probe_altU_values`), M108 `altU` with period 3
(`probe_altU_period_two`), and M109 `unitRate n = n + 1` (`probe_unitRate_constant`). Equivalence control E17 (`altU`
with its branches swapped, `if n % 2 = 1 then 0 else π`) must NOT be killed.

### 14.4 Results (local, 2026-11-17, after the refresh onto `main` `ade1179` and the renumbering to M87–M94)

`check_lean_gate.sh` (SKIP_CACHE=1): PASS, 869 project declarations audited (P6 included), build warnings 0,
standard axioms only. `lean_mutation_check.py` full run: PASS, statement mutants rejected 58/58, definition mutants
killed 36/36, total 94/94 (lock mutants M87–M94 all caught for the reasons in §14.3), equivalence controls not killed
16/16 (E16 included), typo controls 4/4. pytest (`tools/ci/tests`, `research/lean_gate/tests`): 317 passed at `0141601`, and 360 at the merged tip `9fd50ba`
(which adds #40's study-path tests). Checkers and inventory: rc 0. The M107–M109 / E17 follow-up results are in
§14.6.
(At `a9e0a35`, before the refresh, 2026-11-15: 820 declarations, 47/47, 27/27, 74/74, 12/12, 3/3, pytest 299.
At `e50102c`: 818 declarations, 46/46, 73/73.)

### 14.5 Still open

* The lock is ASSUMED, not derived from the closed loop; this does not prove the engine locks (O1 open).
* At the engine's `α = exp(−dt/T_window)` (`aief_experiment_engine_v1.py` `alpha`, `dt = 0.01`,
  `T_window = 25 / mean(ω) = 17.502917…`, so `α ≈ 0.999429`) the bound `1 − 2α^k` passes `1/2` only from `k = 2427`
  steps; the error factor `α^k` itself is `≤ 1/2` from `k = 1214`. The test reads `dt` and the ω list from the engine
  source (N4). This is a rate, not a claim about any run.
* Exact reals; not float64 or the Python code. `AUD-RATELAW stays UNEXPLAINED`.

### 14.6 Results of the #41 note-1 follow-up (local, 2026-11-17, on `main` `c9863e1`)

`check_lean_gate.sh` (SKIP_CACHE=1): PASS, 894 project declarations audited (`probe_altU_values` added), build
warnings 0, standard axioms only. `lean_mutation_check.py` full run: PASS, statement mutants rejected 70/70,
definition mutants killed 39/39 (M107 killed by `probe_altU_values`, M108 by `probe_altU_period_two`, M109 by
`probe_unitRate_constant`), total 109/109, equivalence controls not killed 17/17 (E17 included), typo controls 4/4.
(The mutation run came before one doc-comment line in `FrequencyLock.lean` was rewrapped to fix a
line-length warning. The rewrap changes no code, and the gate above ran after it.)

## 15. DelayRoots (branch `research/lean-gate-delay-roots`, from `main` `871417d`; merge-refreshed on 2026-11-17 onto `main` `16c7893`, which contains P6 (#39, §13) and the frequency lock (#41, §14); numbered after both)

### 15.1 What it is
`lean/AIEFGateCore/AIEFGateCore/DelayRoots.lean` (namespace `AIEFGate.DelayRoots`) is pure algebra. It covers the characteristic polynomials in Arena_Researcher_06020041's cycles 9 and 10, which are unverified inbox material (Auditor review on `audit-inbox` @ `4ee9fe5`):

- `symRoot_eq_one_or_lt`: for 0 < a < 1, every root of λ^(d+1) − (1−a)λ^d − a is 1 or has |λ| < 1.
- `symRoot_one`: 1 is a root, plus the arithmetic identity (d+1) − (1−a)·d = 1 + a·d. By the power rule that number is P′(1), but the derivative is not formalised, so simplicity of the root is **not** proved.
- `transRoot_lt_one`: for 1 ≤ m, 0 < h and m·h < 1, every root of λ^(d+1) − (1−m·h)λ^d + h has |λ| < 1.
- `projectedSlope_lt_quarter`: if x > C > 0 and ε > 0, then C·ε/(x+ε)² < 1/4. `projectedSlope_lt_quarter_of_C` proves the same without ε > 0 (for ε ≤ 0 the slope is ≤ 0).
- Positive instances at delay d = 2: `symRoot_instance_d_two` (a = 1/2) and `transRoot_instance_d_two` (m = 1, h = 1/2).
- Key lemma `eq_one_of_norm_ge_one_of_near`: if |z| ≥ 1, c > 0 and |z − c| ≤ 1 − c, then z = 1.

**Not covered:** that these polynomials are the correct linearisation of the engine step; the existence of the cycle 8 rotating orbit; the projected orbit's non-differentiable tie; heterogeneous ω; production runs. Nothing here supports any AIEF-1.4 claim.

### 15.2 Mutants M95–M106 (statement mutants, numbered after P6 and phaselock; first written as M92–M103 and renumbered by +3 on the refresh onto main `16c7893`, which carries phaselock M87–M94)
| Mutant | Change | Refuted by |
|---|---|---|
| M95 | `symRoot_eq_one_or_lt`: `a < 1` := True | a = 2, d = 1, root −2 |
| M96 | `symRoot_eq_one_or_lt`: conclusion drops `z = 1 ∨` | the root 1 |
| M97 | `transRoot_lt_one`: `1 ≤ m` := True | m = 0, h = 3, d = 0, root −2 |
| M98 | `transRoot_lt_one`: `m h < 1` := True | m = h = 1, d = 0, root −1 (d = 0 is outside Arena's d ≥ 1; M103 has a d = 1 witness) |
| M99 | `projectedSlope_lt_quarter`: `C < x` → `C ≤ x` | C = ε = x = 1, slope exactly 1/4 |
| M100 | `symRoot_eq_one_or_lt`: `0 < a` := True | a = −2, d = 1: P = (λ−1)(λ−2), root 2 |
| M101 | `transRoot_lt_one`: `0 < h` := True | m = 1, h = 0, d = 0: Q = λ − 1, root 1 |
| M102 | `symRoot_eq_one_or_lt`: `a < 1` → `a ≤ 1` | a = 1, d = 1: P = λ² − 1, root −1 |
| M103 | `transRoot_lt_one`: `m h < 1` → `m h ≤ 1` | m = h = 1, d = 1: Q = λ² + 1, root i |
| M104 | `projectedSlope_lt_quarter`: `0 < C` and `0 < ε` := True | C = ε = −1, x = −1/2 (x > C): slope 4/9 |
| M105 | `projectedSlope_lt_quarter_of_C`: `0 < C` := True | C = ε = −1, x = −1/2 (x > C): slope 4/9 |
| M106 | `projectedSlope_lt_quarter_of_C`: `C < x` → `C ≤ x` | C = ε = x = 1: slope exactly 1/4 |

M100–M104 come from Researcher 001's audit of `ae2c25a` (blocker B1 and note N1). The earlier text here said
0 < a had "no simple witness" and 0 < h failed "only at the boundary"; both were wrong (M100, M101). M105–M106 come
from Researcher 001's audit of `cce534d` (note N2): the C-only variant has its own two load-bearing hypotheses.
The two d = 2 instances show the hypotheses can be met; they do not claim any root exists (N3).

**Not mutated, with the reason:**
- `0 < ε` alone, and `0 < C` alone: each is redundant given the other. With C > 0 and ε ≤ 0, or ε > 0 and C ≤ 0,
  the numerator C·ε is ≤ 0, so the slope is ≤ 0 < 1/4 (proved for the first case as `projectedSlope_lt_quarter_of_C`).
  Dropping both is false (M104).
- `1 ≤ m` weakened to `0 ≤ m`: that is M97 (m = 0).

### 15.2a Dictionary to the engine (NOT proved; informal, from Researcher 001's numerical check)
The Lean variables are free reals. Researcher 001's reading of the engine linearisation around the homogeneous-ω orbit
is m = N − 1, h = dt·b·cos(Ω·τ), a = m·h, ε = scale_epsilon, C = capacity, x = (N − 1)·β. Researcher 001 numerically
confirmed that the engine's phase-block spectrum is the roots of P together with N − 1 copies of the roots of Q for 5
(N, d) cases. The block-triangular structure of the EMA/weight part is **not** verified, and nothing in this file
claims it. Nothing here connects the Lean statements to the engine code.

### 15.3 Tests
`research/lean_gate/tests/test_lean_gate_delayroots.py` checks:
- that the module is imported and hash-pinned, with no escape hatches, and that `#print axioms` lines are present;
- the exact shape of M95–M106 (selected by file);
- the witness roots, re-checked in exact rational arithmetic, and the ε ≤ 0 redundancy numerically.

The pins move as follows (after the 2026-11-17 refresh onto `16c7893`): P4b `len(MUTANTS)` goes from 58 to 70, and P5 `N_STATEMENT_MUTANTS` from 58 to 70, so `TOTAL_MUTANTS` goes from 94 to 106 (`N_DEF_MUTANTS` stays 36). `test_lean_gate_c016.py` pins the same totals. (Before the refresh, on `871417d`: 41 to 51, total 76.)

### 15.4 Results (local, 2026-11-15; refreshed 2026-11-17)
- First version (`ae2c25a`): `SKIP_CACHE=1 ./check_lean_gate.sh` PASS, 807 declarations, 0 warnings, standard axioms only. Full mutation run: 46/46 statement mutants rejected, 25/25 definition mutants killed, 11/11 equivalence controls not killed, 3/3 typo controls flagged invalid, RESULT PASS. pytest 297 passed.
- After Researcher 001's audit (M100–M104, `projectedSlope_lt_quarter_of_C`, the two d = 2 instances, `#print axioms`): gate PASS, **818 declarations**, standard axioms only. Full unfiltered mutation run: **51/51 statement** (the one name-reference note is M31's, pre-existing), **25/25 definition**, 11/11 equivalence controls not killed, 3/3 typo controls flagged invalid, RESULT PASS. pytest 299 passed; all repository checkers rc 0.
- After the merge-refresh onto `main` `16c7893` (P6 #39, study-path #40, frequency lock #41) and the renumbering to M95–M106: gate PASS, **893 declarations**, standard axioms only. Full mutation run: **70/70 statement**, **36/36 definition**, **106/106 total**, 16/16 equivalence controls not killed, 4/4 typo controls flagged invalid, RESULT PASS. pytest 367 passed; all repository checkers rc 0.

## 16. Arena intake: CommonRootSimple and EngineStepRef (branch `research/lean-gate-arena-intake`, from `main` `d2a62b7`; numbered after §15 and the #41 follow-up M107–M109 / E17)

### 16.1 What it is
Two Lean files deposited by Arena_Researcher_06020041 on `audit-inbox` (unverified inbox material), taken in by
Auditor Seat 002 and compiled only with networking off (`unshare -rn lake build`). The file headers were
rewritten (to the repository copyright block and a module doc, so the header linter passes), `EngineStepRef.lean`
gained one import line (`Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic`, for `Real.pi` in the probes), and
probes, `false_*` witnesses and `#print axioms` lines were appended before `end`. Every deposited definition and
proof is byte-identical (Researcher 001's audit of `d3dc332`, #44 note N2). Deposit paths on `audit-inbox`:
`AIEFS_common_root_package/` @ `380052e` (not the shorter `AIEFS_cycle13/` copy) and
`AIEFS_engine_step_ref_revised/` @ `8fc0d24`.

`lean/AIEFGateCore/AIEFGateCore/CommonRootSimple.lean` (cycle 13, `audit-inbox` @ `380052e`, namespace
`AIEFGate.CommonRootSimple`), pure algebra over ℂ for P(λ) = λ^(d+1) − (1−h)λ^d − h:
- `common_root`: 1 is a root for every real h and natural d.
- `derivative_at_one`: P′(1) = 1 + d·h (the derivative is now formalised, closing the gap noted in §15.1).
- `root_multiplicity_one`: for 0 < h, the root 1 is simple.
- `unit_circle_root_unique_and_simple`: for 0 < h < 1, any root with |z| = 1 is z = 1 and is simple.
- Counterexamples kept from the deposit: `negative_parameter_double_*`, `upper_boundary_other_unit_root`, `derivative_probe`.

`lean/AIEFGateCore/AIEFGateCore/EngineStepRef.lean` (cycle 21, `audit-inbox` @ `8fc0d24`, namespace
`AIEFGate.EngineStepRef`), a fixed-weight reference model of one phase step:
- `clippedWeight b = max 0 b`; `phaseHead` = x 0 i + dt·(ω + Σ_{j ≠ i} clippedWeight b · sin(x d j − x 0 i));
  `phaseStep` uses the head at slot 0 and shifts slot k > 0 to the old slot k − 1; `orbitPath` is the rotating
  history θ − k·dt·Ω plus t·v.
- `orbit_invariant`: if Ω = ω + (n−1)·clippedWeight b·sin(−d·dt·Ω), the rotating history advances by +dt·Ω (unwrapped).
- `neighbor_derivative`, `head_derivative_raw`, `head_derivative_block`, `phase_step_head`, `history_derivative`:
  real derivatives in t at t = 0 (HasDerivAt) of the step along the orbit, giving the block
  (1 − (n−1)·dt·b·cos(d·dt·Ω))·v₀ᵢ + dt·b·cos(d·dt·Ω)·Σ_{j≠i} v_d j for the head and v_(k−1) for k > 0.
- Concrete probes from the deposit: `two_node_probe`, `self_coupling_probe`, `adjacent_history_probe`, `clipping_probe`.

**Engine citations (checked by Auditor against `aief_experiment_engine_v1.py` at `d2a62b7`, lines 789–797, 830–839,
841–844; pinned in `test_lean_gate_arena_intake.py`):** the coupling uses the clipped, already-updated weight
matrix with a zero diagonal (no self coupling), the delayed neighbour phase, and the current own phase; the history
is appended then its oldest entry dropped (engine `history[0]` is the OLDEST entry, length delay_steps + 1). The Lean
slot index k counts steps back from the newest, so Lean slot d is engine `history[0]`; the order is reversed, not wrong.

**Not covered (disclosures):**
- Fixed common off-diagonal weight b, no shuffle, no active projection, no EMA/weight dynamics: this is not the
  adaptive engine, and nothing here says the engine's linearisation equals this block.
- Unwrapped phases: the engine takes θ mod 2π after the step; the Lean model does not (the file says so).
- Existence of Ω solving the orbit equation is **not** proved; `orbit_invariant` takes it as a hypothesis.
- `probe_orbitPath_value` checks a single point (5 − 2·2·3 + 7·2 = 7; the flipped sign gives 31), so it pins the
  sign of the k·dt·Ω term (M129) and little else.
- Nothing here supports any AIEF-1.4 claim.

### 16.2 Statement mutants M110–M118 (rule as §5: real proof failure, refuted by a proved negation, term-specific)
| Mutant | Change | Refuted by |
|---|---|---|
| M110 | `root_multiplicity_one`: `0 < h` := True | `false_multiplicity_no_pos` (d = 1, h = −1: double root at 1) |
| M111 | `unit_circle_root_unique_and_simple`: `h < 1` := True | `false_unit_root_no_upper` |
| M112 | `unit_circle_root_unique_and_simple`: `0 < h` := True | `false_unit_root_no_pos` |
| M113 | `derivative_at_one`: `1 + d·h` → `1 + h` | `false_derivative_no_delay` |
| M114 | `orbit_invariant`: `+ dt·Ω` → `− dt·Ω` | `false_orbit_backward` |
| M115 | `orbit_invariant`: orbit equation := True | `false_orbit_no_frequency` |
| M116 | `head_derivative_block`: `0 < b` := True | `false_block_no_pos` (via `clipping_probe`, `HasDerivAt.unique`) |
| M117 | `history_derivative`: `v (k−1) i` → `v k i` | `false_history_no_shift` (via `adjacent_history_probe`) |
| M118 | `neighbor_derivative`: `v d j` → `v 0 j` | `false_neighbor_current_slot` |

### 16.3 Definition mutants M119–M129 (rule as §11.3: build fails, no name-reference/parse error, a declared value probe fails)
| Mutant | Change | Killed by |
|---|---|---|
| M119 | `commonPoly`: constant term sign flipped | `probe_commonPoly_eval_d1`, `probe_commonPoly_eval_d2` |
| M120 | `commonPoly`: middle power X^(d+1) | same |
| M121 | `commonPoly`: middle coefficient 1 + h | same |
| M122 | `clippedWeight`: clip dropped | `probe_clippedWeight_values` |
| M123 | `clippedWeight`: `min` for `max` | same |
| M124 | `phaseHead`: self coupling (sum over all j) | `probe_phaseHead_value` |
| M125 | `phaseHead`: reads the current slot of the neighbour | same |
| M126 | `phaseHead`: sine argument reversed | same |
| M127 | `phaseHead`: dt on ω only | same |
| M128 | `phaseStep`: history not shifted | `probe_phaseStep_values` |
| M129 | `orbitPath`: sign of k·dt·Ω flipped | `probe_orbitPath_value` |
| M130 | `phaseHead`: raw `b` instead of `clippedWeight b` (#44 note N1) | `probe_phaseHead_negative_weight` (b = −1: clipped head 1/2, raw −3/2) |

Equivalence controls (must not be killed): E18 `X^d * X` for `X^(d+1)`; E19 `clippedWeight b * -Real.sin (x 0 i − x d j)`;
E20 `max b 0`. **Disclosure:** E18–E20 make the build fail inside proofs (`unit_circle_root_unique_and_simple`,
`orbit_invariant` / `head_derivative_raw`, `head_derivative_block`) but no value probe fails, so they count as not
killed only through the probe rule. This is proof brittleness, the same situation as Researcher 001's #43 note N1 on E17.

`OPENS` gains `open Polynomial (derivative)`, `open AIEFGate.CommonRootSimple (commonPoly)` and
`open AIEFGate.EngineStepRef (clippedWeight phaseHead phaseStep orbitPath)` so refutation files see the
file-local definitions; a grep found no name clashes.

**M130 (#44 note N1).** Researcher 001 found that `probe_phaseHead_value` runs at b = 1/2 > 0, where the clip does
nothing, so a `phaseHead` that bypassed `clippedWeight` (the engine's `np.maximum`) survived every probe (their F4).
M122/M123 only mutate `clippedWeight`'s own body. `probe_phaseHead_negative_weight` evaluates the head at b = −1, where
the clipped coupling is 0 and the head is dt·ω = 1/2; M130 pins it.

**Not mutated, with the reason (#44 note N3):** `hn : 1 ≤ n` in `orbit_invariant` and `head_derivative_block` is
redundant, because `i : Fin n` already forces n ≥ 1. Dropping it leaves a true statement that nothing can refute
(Researcher 001's S3/S4 builds fail only inside the proofs), so it is not a statement mutant.

### 16.4 Tests and pins
`research/lean_gate/tests/test_lean_gate_arena_intake.py` checks imports and hash pins, no escape hatches, an axioms
print for every theorem, the exact shape of M110–M129 and E18–E20, the `OPENS` entries, the probe and witness values
in exact arithmetic, and the engine citations above. Pins move: P4b `len(MUTANTS)` 70 → 79; P5 `N_STATEMENT_MUTANTS`
70 → 79, `N_DEF_MUTANTS` 39 → 50, total 109 → 129, equivalence controls 17 → 20; c016 unique controls 21 → 24. M130 (#44 N1) then moves `N_DEF_MUTANTS` 50 → 51 and the total 129 → 130.

### 16.5 Results
Local, 2026-11-19, on `main` `d2a62b7`: `unshare -rn lake build` 2341 jobs, 0 warnings. `SKIP_CACHE=1 ./check_lean_gate.sh`
PASS, **947 declarations**, standard axioms only (propext, Classical.choice, Quot.sound). Full unfiltered mutation run:
**79/79 statement** mutants rejected (the one name-reference note is M31's, pre-existing), **50/50 definition** mutants
killed, **129/129 total**, 20/20 equivalence controls not killed, 4/4 typo controls flagged invalid, RESULT PASS.
pytest 373 passed; all repository checkers rc 0 after the inventory rebuild.

After the #44 follow-up (M130, on `main` `63e06d7`): gate PASS, **948 declarations**, standard axioms only; full unfiltered
mutation run **79/79 statement**, **51/51 definition** (M130 killed by `probe_phaseHead_negative_weight`), **130/130
total**, 20/20 equivalence controls not killed, 4/4 typo controls flagged invalid, RESULT PASS; pytest 373 passed;
all repository checkers rc 0 after the inventory rebuild.

## 17. Arena bundle intake: 12 modules of the 2026-11-25 MERGE_MANIFEST (branch `research/arena-bundle`, from `main` `7865ab19`; numbered after §16 and M130)

### 17.1 What it is
The owner approved a bundle PR for the accepted Arena_Researcher_06020041 candidates listed in
`audit_inbox/Arena_Researcher_06020041/2026-11-25_MERGE_MANIFEST/` on `audit-inbox` @ `41335f0` (unverified inbox
material). Twelve Lean modules are taken in, by the owner's choice: ReachableQueue (D7), EmaNearUnit (D7),
MatrixPhaseBridge (D6, prerequisite of QueueComposition), QueueComposition (D8), EmaWrapInvariant (D9),
CausalEMATracking (D9), EMAFiniteSum (D11), TransientBridge (D13), TransientParameter (D14), WindowMax (D15),
HeteroStepRef and HeteroGuard (D17). **CoherenceSpeedLimit (D10) is deliberately not taken in**: its
`trace_motion_min` overlaps `CoherenceMotion.trace_step_abs_le_min` already on main. The manifest's `build_bundle.sh`
and other deposited scripts were **not executed**; the Lean was compiled only with networking off
(`unshare -rn lake build`).

Each staged file was checked against the manifest's `source_inventory.tsv` sha256 (and the inbox copy) before
editing. Edits, all additive: the repository copyright block, a module doc (with the verdict and the deposit sha256
prefix), and an appended `/-! ### ...(SPEC §17)` section with value probes, `false_*` witnesses, the helper
`CausalEMATracking.far_start`, and `#print axioms` lines for every new theorem and for five deposited theorems that
had none (`QueueComposition.consistent_transfer`, `initialized_consistent`, `TransientBridge.mode_sum`,
`energy_nonneg`, `TransientParameter.mode_sum`). MatrixPhaseBridge's SPDX comment was replaced by the block (its
session date is kept in the doc; its caveat "lead-note date conflicts, see note" was at first dropped and is restored
by the audit follow-up, §17.7 N4; the deposit file itself contains no such note, so the date is unverified). **Every deposited statement and proof is unchanged**:
`test_lean_gate_arena_bundle.py` strips the added parts and pins the sha256 of the remaining non-blank lines, which
equals that of the deposit.

What the modules say (exact reals; fixed weights; none of it supports an AIEF-1.4 claim):
- `ReachableQueue`: an engine-order finite queue (index 0 oldest) whose drop-oldest/append shift keeps "current phase
  = newest slot on the circle" for every reachable state from a consistent start, for any next-phase rule.
- `MatrixPhaseBridge`: a fixed supplied matrix `W` in the phase head; the engine-shaped step agrees with the matrix
  reference on the circle under that consistency; a uniform zero-diagonal `W` reduces to `EngineStepRef.phaseHead`.
- `QueueComposition`: the finite queue viewed as the newest-first bridge state; from a constant initial queue every
  fixed-`W` iterate agrees with the matrix reference on every retained circle coordinate.
- `EmaNearUnit` / `EmaWrapInvariant`: if every past input projects at least `1 − δ` (or a wrap-invariant cosine
  condition holds), the zero-start coherence trace has norm `≥ 1 − ε` with budget `α^N + δ ≤ ε`. The phase spread is
  a HYPOTHESIS; locking is not proved.
- `CausalEMATracking` / `EMAFiniteSum`: the EMA error obeys `e(n+1) = α e(n) − Δinput`, so `‖e n‖ ≤ α^n ‖e 0‖ +
  Σ α^(n−1−k) |drift k|` with the delayed-increment drift, for `0 ≤ α`.
- `TransientBridge` / `TransientParameter`: two-slot energy of one mean-zero mode (`N = 3`, `d = 1`); derivative link to
  `EngineStepRef.phaseStep`, root stability for `0 < c < 1`, one-step and (at `c = 1/4`) all-time energy bounds.
- `WindowMax`: mean-zero window max-norm invariant for `N ≥ 2`, `0 ≤ c ≤ 2/N`; growth witness above the threshold
  (linearised at the in-phase frozen state, Ω = 0: `reference_link` is the derivative along `orbitPath … 0 1`).
- `HeteroStepRef` / `HeteroGuard`: fixed `B`, all perturbations, window invariant under `dt ≥ 0`, `B ≥ 0`,
  `dt·row_i(B) ≤ 1`; the exact-real gap guard implies the row condition; growth witness when a row fails
  (linearised at the in-phase frozen state, Ω = 0: `weighted_step_derivative` is taken along `orbitPath … 0 θ`).
- Scope of both (audit note N3): "all perturbations" means all perturbations of that one linearised map, iterated. It
  matches an engine linearisation along an orbit only when `cos(d·dt·Ω) = 1`; the engine's heterogeneous ω has no such
  in-phase orbit. `HeteroGuard.engine_constants_safe` is exact-rational algebra on the default constants
  (`dt·cap ≈ 0.0063 ≪ 1`), not a statement about runs.

**Engine citations** (MatrixPhaseBridge lines 823, 830–839, 836–839, 841–844; HeteroStepRef lines 830–839) were
checked against `aief_experiment_engine_v1.py` (sha `ca4593fd…`, unchanged) and are pinned in the test.

**Not covered (disclosures):** no float64, no `mod 2π` in the reference heads (MatrixPhaseBridge's `wrap` only),
no adaptive B, shuffle, projection or gate dynamics; the Transient Euclidean gains are largely queue-copy artifacts
and must not be cited as engine amplification (MERGE_MANIFEST); TransientParameter's range necessity and an all-time
general-`c` bound are not proved; `DelayRoots` is imported by TransientParameter but unused.

### 17.2 Statement mutants M131–M156 (rule as §5)
| Mutant | Change | Refuted by |
|---|---|---|
| M131 | `ReachableQueue.reachable_consistent`: consistency := True | `false_reachable_no_consistent` (`bad`, t = 0) |
| M132 | `view_shift`: `k > 0` := True | `false_view_shift_no_pos` (k = 0 reads the appended value) |
| M133 | `QueueComposition.consistent_transfer`: queue invariant := True | `false_transfer_no_consistent` |
| M134 | `MatrixPhaseBridge.matrix_circle_bridge`: consistency := True | `false_bridge_no_consistent` |
| M135 | `matrix_to_scalar`: `Uniform` := True | `false_scalar_no_uniform` (via `nonuniform_counterexample`) |
| M136 | `EmaNearUnit.near_unit`: budget without `α^N` | `false_near_unit_no_startup` (N = 0) |
| M137 | `near_unit`: `0 ≤ δ` := True | `false_near_unit_no_delta_nonneg` (δ = −1) |
| M138 | `EmaWrapInvariant.near_unit_circular_spread`: budget without `α^N` | `false_circular_no_startup` |
| M139 | `CausalEMATracking.tracking_step_bound`: `0 ≤ α` := True | `false_step_bound_no_nonneg` (α = −1, C0 = 10) |
| M140 | `delayed_tracking_bound`: `0 ≤ α` := True | `false_delayed_bound_no_nonneg` |
| M141 | `EMAFiniteSum.budget_eq_finite_sum`: reversed powers `α^k` | `false_finite_sum_reversed` (4 ≠ 1) |
| M142 | `budget_eq_finite_sum`: start without `α^n` | `false_finite_sum_no_start_decay` |
| M143 | `TransientBridge.one_step_bound`: factor 1 | `false_one_step_factor_one` (5/4) |
| M144 | `two_step_bound`: factor 1/4 | `false_two_step_quarter` (37/64 > 1/2) |
| M145 | `all_steps_bound`: factor 1 | `false_all_steps_factor_one` |
| M146 | `TransientParameter.stable_roots`: `c < 1` := True | `false_stable_no_upper` (c = 2, root −1) |
| M147 | `stable_roots`: `0 < c` := True | `false_stable_no_pos` (c = 0, root 1) |
| M148 | `one_step_bound`: `c ≤ 1` := True | `false_one_step_no_upper` (energy 10) |
| M149 | `WindowMax.window_step`: `n·c ≤ 2` := True | `false_window_step_no_threshold` (c = 4/5: 7/5) |
| M150 | `window_all_steps`: `n·c ≤ 2` := True | `false_window_all_no_threshold` |
| M151 | `coefficient_bound`: `2 ≤ n` := True | `false_coefficient_no_size` (n = 1, c = 1) |
| M152 | `HeteroStepRef.window_step`: row condition := True | `false_window_step_no_row` (head −3) |
| M153 | `window_step`: `0 ≤ B` := True | `false_window_step_no_nonneg` (row sums 0, head 3) |
| M154 | `window_step`: `0 ≤ dt` := True | `false_window_step_no_dt` (dt = −1, head 3) |
| M155 | `HeteroGuard.guarded_window_all_steps`: cap := True | `false_guarded_no_cap` |
| M156 | `guarded_window_all_steps`: `0 < q` := True | `false_guarded_no_q` (q = 0) |

**Audit follow-up M191–M201 (Researcher 001 note N5, §17.7).** Statement mutants for deposited theorems that had
none. Rule as §5. **Predeclared in the commit that adds them, before any run: every one is expected REJECTED** (none
is expected to survive; a survivor would be reported UNEXPLAINED, not moved to `KNOWN_SURVIVORS`).

| Mutant | Change | Refuted by | Predeclared |
|---|---|---|---|
| M191 | `EmaNearUnit.trace_projection_bound`: startup factor `(1 − α^N)` dropped | `false_projection_no_startup` (N = 0, L = 1) | REJECTED |
| M192 | `trace_norm_bound`: startup factor `(1 − α^N)` dropped | `false_norm_no_startup` (N = 0, L = 1) | REJECTED |
| M193 | `near_unit_of_phase_spread`: budget without `α^N` | `false_spread_no_startup` (N = 0, β = 0, ε = 0) | REJECTED |
| M194 | `EMAFiniteSum.delayed_tracking_sum`: `0 ≤ α` := True | `false_delayed_sum_no_nonneg` (α = −1, C0 = 10, n = 1) | REJECTED |
| M195 | `ReachableQueue.step_reachable_consistent`: consistency := True | `false_step_reachable_no_consistent` (`bad`, t = 0) | REJECTED |
| M196 | `QueueComposition.finite_abstract_step`: reads slot 0 for `history k` | `false_finite_step_head_slot` (`probeState`, dt = 0, k = 1: 1 ≠ 0) | REJECTED |
| M197 | `MatrixPhaseBridge.matrix_head_direction`: factor `cos(d·dt·Ω)` dropped | `false_head_direction_no_cos` (Ω = π: derivative −1, not 1) | REJECTED |
| M198 | `TransientBridge.after_first_bound`: factor 1/4 | `false_after_first_quarter` (p = (1, −1): 37/64 > 1/2) | REJECTED |
| M199 | `TransientBridge.eigenmode_stable`: `v ≠ 0 ∨ w ≠ 0` := True | `false_eigenmode_no_nonzero` (v = w = z = 0) | REJECTED |
| M200 | `TransientParameter.eigenmode_stable`: `v ≠ 0 ∨ w ≠ 0` := True | `false_param_eigenmode_no_nonzero` (c = 1/2, z = 1) | REJECTED |
| M201 | `HeteroStepRef.window_all_steps`: row condition := True | `false_window_all_no_row` (t = 1, head −3) | REJECTED |

**Still without a statement mutant** (plain list):
- `QueueComposition.initialized_trajectory_bridge`: not mutable by the current harness. Its statement contains
  `let s := …`, and `theorem_span` / `statement_prop` stop at the first top-level `:=`. A harness change is out of
  scope here. Its two ingredients are mutated: `consistent_transfer` (M133) and `finite_abstract_step` (M196).
- Unconditional identities and value facts, with no hypothesis to drop: `ReachableQueue.shift_consistent`,
  `QueueComposition.initialized_consistent`, `CausalEMATracking.tracking_identity`,
  `TransientBridge.mode_sum` / `TransientParameter.mode_sum`, `spatial_energy`, `energy_nonneg`, `first_step_value`,
  `characteristic_roots`, `reference_mode_link` (both Transient files), `WindowMax.reference_link`,
  `EmaWrapInvariant.arcBound_periodic`, `HeteroStepRef.agrees_main`, `weighted_head_derivative`,
  `weighted_step_derivative`, `guard_row_bound`.
- Counterexamples and closed probes that are themselves the negative facts: `ReachableQueue.bad_breaks_reference`,
  `MatrixPhaseBridge.probeW_mean`, `probeW_nonuniform`, `nonuniform_counterexample`, `inconsistent_counterexample`,
  `EmaWrapInvariant.cross_wrap_angle`, `cross_wrap_good`, `cross_wrap_rejected`,
  `CausalEMATracking.drift_factor_one_probe`, `EMAFiniteSum.oldest_drift_probe`, `reversed_power_counterexample`,
  `TransientParameter.quarter_probe`, `zero_boundary`, `WindowMax.exact_growth_witness`,
  `HeteroStepRef.growth_witness`, `HeteroGuard.engine_constants_safe` (exact-rational algebra on the defaults).
  These are not mutated.

**FILE_OPENS.** The bundle reuses short names (`State`, `Consistent`, `step`, `iterate`, `mode`, `energy`,
`window_step`, `window_all_steps`, ...) in distinct namespaces. Rather than renaming anything, each refutation file
opens only the mutated file's namespace (`FILE_OPENS` in `lean_mutation_check.py`; `refute` gained a `preamble`
argument; EMAFiniteSum also opens CausalEMATracking for `budget`). No theorem was renamed; the full build imports all
modules together with no clash.

### 17.3 Definition mutants M157–M190 (rule as §11.3)
| Mutants | Definition | Changes | Killed by |
|---|---|---|---|
| M157–M160 | `ReachableQueue.shift`, `reverseIndex`, `head` | no shift; no append; view not reversed; head reads newest | `probe_shift_values`, `probe_view_values`, `probe_head_value` |
| M161–M162 | `QueueComposition.abstractState`, `initState` | view not reversed; zero initial queue | `probe_abstractState_values`, `probe_initState_values` |
| M163–M167 | `MatrixPhaseBridge.matrixHead`, `engineStep`, `refInput` | current slot; sine reversed; no shift; slot 0 in the step head; history at slot 0 | `probe_matrixHead_value`, `probe_engineStep_shift`, `probe_engineStep_head`, `probe_refInput_values` |
| M168 | `EmaWrapInvariant.arcBound` | inequality reversed | `probe_arcBound_values` |
| M169–M171 | `CausalEMATracking.budget` | `(1−α)` on drift; no decay; zero start | `probe_budget_values` |
| M172–M176 | `TransientBridge.stepSize`, `step`, `energy` | 1/3; `1 − c`; `+ c·p.2`; unshifted; one slot | `probe_step_values`, `probe_energy_value` |
| M177–M181 | `TransientParameter.step`, `energy`, `mode` | `1 − c`; `+ c·p.2`; unshifted; one slot; mode not mean-zero | `probe_step_values`, `probe_energy_value`, `probe_mode_values` |
| M182–M185 | `WindowMax.next` | `n` for `n − 1`; `+ c·v d`; slot 0 for `d`; unshifted | `probe_next_values` |
| M186–M190 | `HeteroStepRef.linearStep`, `row`, `phaseHeadW` | `1 + dt·row`; slot 0 in the sum; unshifted; row without diagonal; head reads current slot | `probe_linearStep_values`, `probe_phaseHeadW_value` |

Equivalence controls (must not be killed): E21 `v d * c` for `c * v d` in `WindowMax.next`; E22 `1 − c − c` for
`1 − 2c` in `TransientParameter.step`; E23 the `budget` sum commuted. EmaNearUnit, EMAFiniteSum and HeteroGuard
define nothing of their own, so they have statement mutants only.

### 17.4 Merge note: WindowMax and HeteroStepRef are complementary, not contradictory
Write `c = dt·b` for a uniform off-diagonal weight `b`. **HeteroStepRef** needs `dt·row_i(B) ≤ 1` for every row,
which in the uniform case is `(N−1)·c ≤ 1`, i.e. `c ≤ 1/(N−1)`; it then bounds the window for **all** perturbations.
**WindowMax** allows the larger range `c ≤ 2/N`, but only for **mean-zero** spatial modes. Since `1/(N−1) ≤ 2/N` for
every `N ≥ 2` (equal at `N = 2`), the two never conflict: between the thresholds a mean-zero mode is still bounded
while a non-mean-zero window can grow (HeteroStepRef's `growth_witness`; checked at `N = 3`, `c = 3/5` in the test).
**TransientBridge and TransientParameter are included per the owner's choice of 12 files**, although the manifest
recommended archiving them; their bounds are correct exact-real facts but say nothing about engine amplification.

### 17.5 Tests and pins
`research/lean_gate/tests/test_lean_gate_arena_bundle.py`: imports and hash pins, CoherenceSpeedLimit absent,
deposit bodies unchanged (pinned digests), no escape hatches, an axioms print for every theorem, the exact shape of
M131–M190 (and M191–M201, §17.7) and E21–E23, `FILE_OPENS` (one bundle namespace each except EMAFiniteSum, which
opens CausalEMATracking and EMAFiniteSum; none in the global `OPENS`), and the engine citations.
`test_probe_and_witness_values_exact` reads the Lean sources: it pins the Python models to the text of `next`,
`linearStep`, `row`, `step`, `stepSize`, `energy` and `budget`, checks that each probe statement's right-hand side
equals the model value, checks the mutant values named in the `probe_next_values` docstring, and checks each
witness instance (`have h := H …`) and the violation it gives. `test_window_max_and_hetero_are_complementary` parses
the §17.4 thresholds, the `N ≥ 2` range and the `N = 3`, `c = 3/5` example from this SPEC text and checks them
against the hypotheses of `HeteroStepRef.window_step`, `WindowMax.coefficient_bound` / `window_step` and
`growth_witness` as written in Lean. (Before the §17.7 follow-up these two tests recomputed constants in Python only
and could not fail when the Lean or the SPEC changed; audit note N1.) Pins move: P4b `len(MUTANTS)` 79 → 105;
P5 `N_STATEMENT_MUTANTS` 79 → 105, `N_DEF_MUTANTS` 51 → 85, total 130 → 190, equivalence controls 20 → 23; c016
unique controls 24 → 27 and M131–M190 numbered; the stubbed full-run test's `refute` takes the new `preamble` argument.

### 17.6 Results (2026-11-26 GMT)

- `SKIP_CACHE=1 unshare -rn ./check_lean_gate.sh`: RESULT PASS. Build 2353 jobs, 0 warnings;
  SHA256SUMS verified (42 files); escape-hatch scan 38 files, 0 hits; step 7 audited
  **1188 project declarations**, standard axioms only (propext, Classical.choice, Quot.sound).
- Full unfiltered `lean_mutation_check.py` (offline): **105/105 statement** rejected (the one
  name-reference note is M31's, pre-existing), **85/85 definition** killed, **190/190 total**,
  23/23 equivalence controls not killed, 4/4 typo controls flagged invalid, RESULT PASS.
- pytest: `research/lean_gate/tests` 193 passed, `tools/ci/tests` 246 passed (439 total);
  all repository checkers rc 0 after the inventory rebuild.
- Red-team of `test_lean_gate_arena_bundle.py`: 11 wrong variants (edited deposit proof, changed
  probe value, dropped `#print axioms`, inserted `sorry`, dropped root import, added
  CoherenceSpeedLimit, widened a FILE_OPENS entry, dropped M190, wrong refuter name, moved engine
  citation, dropped E23), each applied to a copy outside the repo; all 11 caught.
- No mutants dropped; no declarations renamed; deposited proofs and statements unchanged.

### 17.7 Audit follow-up (branch `fix/arena-bundle-audit-notes`, from `main` `daa977ac`)
Researcher 001's independent audit of `research/arena-bundle` @ `82a5a1f` (non-author) returned **CLEAN WITH NOTES**
(`audit_inbox/briefing/REVIEW_2026-11-25_r001_arena-bundle_82a5a1f.md` on `audit-inbox`). PR #52 merged before this
follow-up. Its notes, and what this branch does about each:
- **N1 (test honesty).** `test_probe_and_witness_values_exact` and `test_window_max_and_hetero_are_complementary`
  read no Lean file and no SPEC text, so they could not fail when a probe value or the §17.4 thresholds changed.
  Both now parse what they are named after (§17.5). **Correction to §17.6 (add-only):** the "all 11 caught" red-team
  there partly relied on a stale `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` pin. The red-team script did not regenerate
  the sums after each Lean edit, so at least the changed-probe-value, inserted-`sorry` and edited-deposit-proof
  variants were also, or only, caught by the file-hash pin. The new red-team regenerates the sums after every edit.
  Its baseline label, which printed `SURVIVED (BAD)` for a passing baseline, is corrected.
- **N2 (wording).** The `lean_mutation_check.py` comments said a refutation never opens two bundle namespaces.
  EMAFiniteSum opens two, CausalEMATracking and EMAFiniteSum, which share no names. The comments now say so.
- **N3 (scope).** README row and §17.1 now say that WindowMax and HeteroStepRef are linearised at the in-phase frozen
  state (Ω = 0), with what "all perturbations" does and does not cover.
- **N4 (provenance).** The MatrixPhaseBridge module doc again carries the deposit's "lead-note date conflicts, see
  note" caveat, and says that the deposit file contains no such note. This changes the repository header doc only; no
  deposited statement or proof changes (the deposit digest test still passes).
- **N5 (coverage).** Statement mutants M191–M201 are added, each predeclared REJECTED (§17.2). The theorems still
  without a statement mutant are listed in §17.2.
- **N6 (CI time).** See the results below.
- **N7 (info).** Commit identity unchanged by convention; no action.

**Results (2026-11-26 GMT, on commit `c666da6`, which first added M191–M201 with their predeclaration):**
- `SKIP_CACHE=1 STRICT_ORPHANS=1 unshare -rn ./check_lean_gate.sh`: RESULT PASS. Build 2353 jobs, 0 warnings;
  SHA256SUMS verified (42 files); escape-hatch scan 38 files, 0 hits; step 7 audited **1199 project declarations**
  (1188 + the 11 new `false_*` witnesses), standard axioms only (propext, Classical.choice, Quot.sound).
- Full unfiltered `unshare -rn python3 research/lean_gate/lean_mutation_check.py` (19 min 25 s locally): **116/116
  statement** rejected, **85/85 definition** killed, **201/201 total**; 23/23 equivalence controls not killed; 4/4
  typo controls flagged invalid; validator, classifier and statement controls as expected; RESULT PASS, rc 0. All 11
  new mutants M191–M201 came out REJECTED, as predeclared. Three statement mutants carry the information-only note
  "build output also has a name-reference/parse error line": M31 (pre-existing) and M199/M200. For M199/M200 this is
  explained: the kept proof does `rcases hne with hv | hw`, which on `hne : True` binds no `hv`, so `Unknown
  identifier hv` appears beside the real failures (`No goals to be solved`). Rejection does not rest on that line.
- pytest: `research/lean_gate/tests` 193 passed; `tools/ci/tests` 246 passed (unittest OK); v4.1 held-event and
  trust-anchor 45 passed; `tests_modular` 60 passed, 2 skipped, 2 xfailed. Every repository checker rc 0
  (lint_claims, hygiene_scan with `--pii` against origin/main and without, check_manifest, check_sha256sums,
  check_artifact_pins, check_modes --strict, check_current_inventory, check_study_paths, check_pinned_restatement,
  verify_inventory_current).
- N1 red-team: 12 wrong variants, each applied to a copy outside the repo with the gate sums regenerated after every
  Lean edit, so the file-hash pin cannot be what catches them. Variants: four probe values changed (WindowMax,
  HeteroStepRef, TransientBridge, CausalEMATracking), a witness instance that no longer violates, a witness factor,
  a probe-docstring mutant value, three §17.4 SPEC edits (`1/(N−1)` → `1/N`, `2/N` → `3/N`, `c = 3/5` → `2/5`), and
  a Lean row-bound change. **All 12 caught**, each by the intended test. Control: the pre-follow-up test file
  (`daa977a`) passes the changed-probe, changed-factor and changed-SPEC variants, which confirms N1.
- **N6 finding (record only; CI unchanged).** Per-step GitHub timings: the whole difference is in the "Lean-gate
  mutation check" step. It took 25 min 20 s on the `82a5a1f` push run, against 17 min 30 s on the PR run for the
  **same sha** about 2.5 hours later, 20 min 20 s on main `daa977a`, and 14 min 53 s on main `8b49f15` (Nov 20, 130
  mutants). `lean-action` setup was 3 min 56 s against about 2.5 min. So 31 min 43 s is mutant growth (130 → 190,
  +46%), plus about 8 minutes of runner variance on identical inputs. There is no sign of a cache miss beyond about
  1.3 minutes of setup. This follow-up adds 11 statement mutants (201 total). The job timeout is 60 minutes, which
  leaves headroom for now, but it should be watched before the next mutant batch.

## 18. H17: `wrapPhase` bridge to Mathlib `toIcoMod` (branch `research/h17-wrapphase-toicomod`, from `main` `daa977a`; Researcher 001 numbering block M700 ff.)

Plan item H17 of audit-inbox `PLAN_2026-11-25_scan_leads.md`, as changed by Auditor Seat 002's review
`REVIEW_2026-11-26_auditor_scan_leads.md` (audit-inbox `b15c5e5`; the review wins where they differ). New module
`AIEFGateCore/WrapBridge.lean` (no edit to `PhaseIncrement.lean`, no new dependency, pinned Mathlib `0df444a`).

- `wrapPhase_eq_toIcoMod`: `Phase.wrapPhase t = toIcoMod Real.two_pi_pos 0 t`, i.e. our floor-based wrap is the
  **[0, 2π)** convention. `wrapPhase_mem_Ico`: `0 ≤ wrapPhase t < 2π`. `wrapPhase_coe_angle`: as a `Real.Angle`,
  `wrapPhase t = t` (corollary only: the coercion forgets the representative, so it cannot discriminate conventions,
  which is why the bridge targets `toIcoMod`, per the review).
- Value probes `probe_wrap_neg_half_pi` (`−π/2 ↦ 3π/2`) and `probe_wrap_zero`.
- Scope: exact reals. The engine wraps with float64 `np.mod(θ, 2*np.pi)` (engine L836). It differs from the Lean
  wrap in two ways (corrected after audit, see §18.2):
  - (a) It reduces modulo fl(2π) = 2π − 2.449e−16, not 2π.
  - (b) It can return its own modulus fl(2π) for x ∈ [−4.440892098500626e−16, 0) (e.g. `np.mod(-1e-20, 2*np.pi)`),
    so float θ ∈ [0, fl(2π)], closed at the top. fl(2π) is inside the real [0, 2π).
  - The phasor is unaffected only up to rounding: exp(i·fl(2π)) = 1 − 2.449e−16·i, and each wrap shifts the real
    phase by about 2.45e−16.
  - **How often production runs hit (b) is UNEXPLAINED (unmeasured).** The witnesses are pinned in
    `tests/test_lean_gate_h17.py`.

Mutant numbering (coordinated with Auditor Seat 002: its follow-up uses M191 ff., its H9(b)+H16 M300 ff.; Researcher
001 uses M400 ff. for H8, M500 ff. for H10, M600 ff. for H12, M700 ff. for H17). H17 adds statement mutants only; no
E or T controls (the existing harness controls apply unchanged). **Predeclared outcome, committed before the run:**

| Mutant | Edit | Refuted by | Predeclared |
|---|---|---|---|
| M700 | `toIcoMod … 0 t` → `toIocMod … (−π) t` ((−π, π] convention) | `false_wrap_toIocMod_neg_pi` (t = −π/2) | KILLED |
| M701 | range `< 2π` → `< π` | `false_wrap_lt_pi` (t = −π/2 ↦ 3π/2) | KILLED |
| M702 | `0 ≤` → `0 <` | `false_wrap_pos` (t = 0) | KILLED |
| M703 | `toIcoMod … 0 t` → `toIcoMod … (−π) t` ([−π, π) convention) | `false_wrap_toIcoMod_neg_pi` (t = −π/2) | KILLED |

The control that shows these can fail: each refutation is a proved `¬` theorem (standard axioms), and the harness's
step (c) re-runs the same term against the unmutated statement, which must fail. A survivor is reported, not deleted.
Counts: statement mutants 105 → 109, total 190 → 194.

### 18.1 Results (local, 2026-11-26 MST, on `main` `daa977a` + this branch)
- Gate (`SKIP_CACHE=1 STRICT_ORPHANS=1`, run under `unshare -rn`): **PASS**. 1197 project declarations audited,
  standard axioms only. The first run failed step 5 on one >100-char line in `WrapBridge.lean`; the line was split and
  SHA256SUMS regenerated before the passing run.
- Mutation harness: **194/194 rejected**. M700–M703 all KILLED as predeclared (refuted by proof, and each term fails on
  the unmutated statement). Typo controls 4/4 flagged invalid; SE1 and ST1 not rejected (good).
- Float witness `np.mod(-1e-20, 2*pi) == 2*pi` holds, i.e. the engine can return its own modulus fl(2π), with the
  +1e-20 negative control. *(The original wording "the engine can produce 2π, outside [0, 2π)" was wrong; see §18.2.)*
  How often this happens in real runs is **UNEXPLAINED** (unmeasured).
- pytest `research/lean_gate/tests`: 197 passed. The 12 CI checkers: all rc = 0.

### 18.2 Audit follow-up (Auditor Seat 002 CLEAN WITH NOTES on `d9a5cad`; Researcher 001, 2026-11-27 MST)
- **N1.** The float result is fl(2π) = 2π − 2.4492935982947064e−16, which is inside the real [0, 2π), not 2π.
  Researcher 001 checked this numerically with a 90-digit rational 2π. The real gaps are (a) the period fl(2π) ≠ 2π
  and (b) `np.mod` returning its own modulus.
  - (b) happens exactly for x ∈ [−4.440892098500626e−16, 0) = [−ulp(fl(2π))/2, 0). This was found by bisection over
    float bit patterns. All 400,001 sampled floats in that range return the modulus. The next float below the range,
    −4.440892098500627e−16, gives 6.283185307179585 < fl(2π).
  - The WrapBridge docstring, the scope bullet above and the §18.1 bullet are reworded. The test pins (a), both ends
    of (b) and the first float outside it.
- **N2.** The phasor claim is now "up to rounding": exp(i·fl(2π)) = 1 − 2.449e−16·i (pinned). How often real runs hit
  (b) stays UNEXPLAINED (unmeasured).
- **N3.** The refuter-exists check is now a word-boundary regex. A copy with `false_wrap_pos` renamed to
  `false_wrap_pos_renamed` fails it (checked, then reverted).
- **N4.** The engine link pins `state.theta = np.mod(`, which occurs exactly once, instead of any `np.mod(`.
- No Lean statement, proof or mutant changed; only the WrapBridge module docstring. SHA256SUMS regenerated.
