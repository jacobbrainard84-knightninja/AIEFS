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
* The mutation check is not run in CI (it needs a built Lean project and about 2 minutes locally).
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
| `preM_eq_convex`, `symM_eq_convex`, `stepM_eq_gateM_convex` | `γ ≠ 0` | port bridge to the cycle-003 proposal form |

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
* The mutation check is not run in CI (it needs a built Lean project and about 5 minutes locally).
* **AUD-RATELAW stays UNEXPLAINED.**


## 11. P5 (branch `research/lean-gate-p5`, from `main` `3c5c0ef`, which contains P4a; **not** based on P4b / PR #26)

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

`MUTANTS` (M1–M23) is unchanged. **M24–M36 are reserved for P4b** (PR #26, `research/lean-gate-p4b`), which appends them to `MUTANTS`. The P5 mutants are
definition mutants (a second kind, see below), numbered **M37–M52**, and live in a separate list `DEF_MUTANTS` so that neither the P4a test (which asserts the
23 statement mutants) nor P4b's `len(MUTANTS) == 36` pin is affected. Exact pin: `test_lean_gate_p5.py` (23 statement + 16 definition = **39** on this branch; 36 + 16 =
**52** after P4b merges: the file's `TOTAL_MUTANTS` and the P4a/P4b pins must be reconciled in whichever of P4b/P5 merges second).

### 11.3 Mutation check: M37–M52 (16 definition mutants)

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

**Negative controls (the run FAILS if any is not as expected):**

* *Equivalence controls* (9; must NOT be killed, i.e. no declared value probe of the file fails): E1 `* 1`, E2 `+ 0`, E3 `id (…)` on `coherenceInput`; E4 `¬ n < d` for `d ≤ n`,
  E5 `u (n − d + 0)` and E6 another proof term for the oldest slot on the 011 delayed read / input read; E7 reordered EMA sum; E8 commuted `‖C i j‖ + ‖C j i‖` in `reported`;
  E9 `(μ + η)` for `(η + μ)` in the drive. (A first version of `probe_input_offset_value` closed its goal with `exact reference_zero …` and was killed by E1/E2, i.e. it
  was itself brittle; it was re-proved by `simp` from the definitions, after which E1/E2 are not killed. This was caught by the controls, which is their purpose.)
* *Typo controls* (3; must be classified INVALID and not killed): T1 `inputPhasorXX`, T2 an unbalanced parenthesis (parse error), T3 `delayedIncrementXX`.
* *Statement-level controls* (2, on M4's statement): SE1 an equivalent rewrite `(1 − dt·γ)` and ST1 a typo `branchScaleXX` must NOT be rejected.
* Known survivor S1 (unchanged, below). Mutants in `KNOWN_SURVIVORS` are run and reported but not counted; a survivor that starts being detected fails the run (stale list).

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

Known survivor **S1** (documented, not counted): dropping the static offset `(ω_i+ω_j)/2·τ` in `PhaseIncrement.inputPhasor` alone is not detected by that file's theorems or value probes
(the offset cancels in the step ratio; Auditor Seat 002's note on 011; no value probe of that file involves `ω` or `τ`). It **is** killed one level up by the value probes
`probe_input_offset_value` and `probe_coherence_values` of `PhaseCoherence.lean` (M43), so "pinned one level up" now rests on value probes, not on `input_engine_convention`.

Result (local, 2026-11-10; full run of the revised rule, `lean_mutation_check.py`): positive controls PASS (8 files), both validator negative controls REJECTED, classifier negative
control PASS; **23/23 statement mutants rejected (M1–M23 unchanged; 0 of them flagged with a name-reference/parse error line)**; statement controls SE1 (equivalent) and ST1 (typo)
NOT rejected; **16/16 definition mutants KILLED by a declared value probe (M37–M52), 39/39 in total; no counted survivor**; **9/9 equivalence controls NOT killed** (E1–E5, E7–E9 fail
only in rewrite lemmas, E6 builds); **3/3 typo controls flagged INVALID** (unknown identifier, parse error, unknown identifier); S1 survives as documented. RESULT PASS.
Under the first version of the rule E1, E2 and E3 would have been scored killed and T1 too (audit of `64f39eb`). The value probes that actually failed are in the table above
(per mutant); rewrite lemmas also failed for most mutants but earn no credit. No mutant, pin or proof was changed after seeing a mutation result, except the re-proof of
`probe_input_offset_value` described under the controls (it was itself brittle: killed by E1/E2) and the pin changes recorded earlier (M48 → `probe_alpha_quarter`, M51/M52 → direct
probes). Limits that remain: a value probe can still fail because its *proof script* is brittle rather than because the value differs; the equivalence controls bound this (nine
rewrites, none kills) but cannot exclude it for other rewrites. The `ω` probes use a node-uniform `ω`, so a mutant replacing `(ω_i+ω_j)/2` by `ω_i` is not in the list (not tested).

### 11.4 Gate results (local, 2026-11-10, Europe/Tirane)

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
* Not done (not on `main`): mutants for the auditor's `Capacity` lemmas `preM_between` and `convex_weights_iff` (PR #27). `Capacity.lean`, `.github/` and `Pinned/` are untouched.

### 11.5 Expected merge conflicts with P4b (PR #26)

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
* No Lean-side statement pin (Lea-style statement hash) in CI; the mutation check is not run in CI (a parallel auditor branch proposes adding it).
* **AUD-RATELAW stays UNEXPLAINED.**
