# Lean work package P1: branch-conditional capacity-gate / controller-kernel identities

Status: NEW unpinned research, branch `research/lean-gate-identities` (from `main` `eb3933c`), 2026-11-09.
Lean project: [`lean/AIEFGateCore`](../../lean/AIEFGateCore). Cross-check: [`lean_gate_crosscheck_v1.py`](lean_gate_crosscheck_v1.py).
Nothing hash-pinned is edited. `registry/claims.csv`, `registry/artifacts.csv` and the ERRATA are not edited.

## 1. What the audit relies on

The rate-law audit (`AI Agent Audits/evidence/scripts/kappa_cycle_kernel.py`, ERRATA E5, E22 on
`research/rate-law-delta-sweep`) measures a one-step multiplier `lam = <(B'(B + δh) - B'(B))/δ, h> / <h, h>` along a
direction `h` in the controller kernel `K = ker A_J`, and compares it with the *state formula* `(1 - γdt) mean(s_J)`.
Its validity rests on an unproved piece of algebra: on a fixed branch, the gate map is affine along `h`, so `lam` does
not depend on `δ`. E22 also reports an "exact branch formula" `(1 - γdt) Σ h_e² s_ctrl(e)` (exact rational evaluation)
that differs from the state formula by 4.04e-13 on the gap component. P1 proves both facts for the real-arithmetic
model, plus the one-sided K3 statements that `lean/AIEFProofs/README.md` lists as not formalised.

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

1. `stepB_add_smul_of_branch` (main): under (B1)-(B4),
   `stepB (B + t h) = stepB B + t (1 − γdt) · branchScale · h` coordinatewise, exactly, where
   `branchScale e = s_ctrl(e)` at the base proposal if the gate fires, else 1. One-step map is affine along `h`.
2. `multiplier_eq_branch_formula`: for `t ≠ 0` the audit estimator equals `(1 − γdt) Σ branchScale_e h_e² / Σ h_e²`,
   independent of `t` (the "constant multiplier along a kernel direction"). This is E22's exact branch formula.
3. `stepB_sub_eq_smul_of_uniform`: if `branchScale ≡ s` on `supp h` (all controller scales equal), `h` is an exact
   eigenvector with eigenvalue `(1 − γdt) s` (the state formula).
4. `eventually_clip_gate`: strict clip and a firing gate test at the base persist for all small `|t|` (B1, B2 are
   open conditions). B4 is *not* open at a tie, which is the point of item 6.
5. `K3_gate_component_multiplier` + `K3_gate_branch_sub_state`: for the AUD-RATELAW gap component
   (nodes `[2,7,11] ↦ 0,1,2`, `J = {0,1}`, node 2 not a controller at either state) along `vRay 2 = (1,−1,−1)`
   (= the pinned `vCtrl`), the multiplier is `(1 − γdt)(min s₀ s₁ + s₀ + s₁)/3`, and
   `branch − state = −(1 − γdt)|s₀ − s₁|/6` exactly. This attributes E22's 4.04e-13 to the tied pair's spread.
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
  E22 shows it is the representation error of `fl(B + δH)`. The cross-check bounds model-vs-engine differences by
  evaluating the Lean definitions in exact rationals on the engine's own float inputs (≤ 5.6e-17 absolute here).
* **Edge vectors, not the 12×12 matrix.** Symmetrisation and the zero diagonal are not modelled; one coordinate per
  unordered pair. Equivalence with the matrix form for symmetric zero-diagonal inputs is argued, not proved.
* **One step, `R` fixed.** `drive` is an input. Justified for B-only perturbations within a step by ERRATA E5;
  nothing is said about later steps, phases, delay, the EMA or branch persistence over time.
* **Exact controllers, no `TIE_TOL`.** The audit treats `|s_i − s_j| ≤ 1e-9` as tied; Lean uses exact order.
  In the cross-check the exact controllers on the edges of the K5 control direction are `{0,1,6}`, whereas TIE_TOL treats all five K5 nodes as tied controllers; the identity is unaffected.
* **Lean division `x/0 = 0`.** Irrelevant to the engine (`ε = 1e-12 > 0`); the cross-check transcription copies it.
* **Not formalised:** the closed-form clique multiplier `λ_k = (1 − γdt)c/(c + dt(kη − γc) + ε)` and the
  finite-time departure of the state formula from it (the 3.26e-10 part in E22); any TIE_TOL / δ_c selection rule;
  the link between `AIEFGate.G3`/`vRay` and the pinned `AIEFProofs` `src3`/`dst3`/`vRay` (same convention, not
  imported, to keep this project free of path dependencies like `AIEFFreezeCore`).

## 5. Red team

Lean (`AIEFGateCore/RedTeam.lean`, concrete K3: dt = 1/10, γ = 1, cap = 1, ε = 0, drive 0, B = 1):
`nonvacuous_plus` (all hypotheses of item 6 satisfiable; response `(1/20) vRay 2`), and proved negations
`false_drop_kernel` (single-edge direction, B3 dropped: 2/3 vs claimed 1), `false_wrong_constant` (factor `1 − γdt`
dropped), `false_two_sided` (B4 dropped: `+vRay` formula at `t = −1/2` gives 1/4 where the map moves 0),
`false_branch_eq_state` (branch ≠ state formula when `s₀ ≠ s₁`).
Mutation check (`lean_mutation_check.py`): five statement mutants of GateMap.lean; all rejected (M1-M3 syntactically,
M4-M5 semantically; see the script docstring).
Python (`lean_gate_crosscheck_v1.py`): fidelity, hypothesis decisions, zero exact residual, engine agreement and four
negative controls (wrong constant, wrong controller set, off-fiber direction, branch crossing). See the results JSON.

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

