# Cycle 8 — an exact rotating solution of the coupled delayed system

**Status:** conditional analytic construction plus finite Python-engine checks; neither Lean-formalized nor independently reviewed. Unlike the earlier assumed-increment result, this construction solves the closed-loop phase, EMA, and weight equations simultaneously on a restricted symmetric state. It is an existence result, not an attraction or stability result.

## Construction

Use N≥2 nodes, identical natural frequency ω, no driver shuffle, and the exact-real idealization of the engine's equations. Put m=N−1, capacity C=(a−δ)/q>0, and assume q>0, γ>0, η>0, dt>0, d≥1, τ=d·dt. All off-diagonal weights are b>0; diagonal weights are zero. Let K=mb. Take any real root Ω of

**Ω = ω − K sin(Ωτ).**

If Kτ<1 this root exists and is unique: F(x)=x−ω+K sin(xτ) is strictly increasing and changes sign on [ω−K,ω+K]. For every integer n define the synchronized circular phase `θₙ = (θ₀+n·dt·Ω) mod 2π`. Set each complex EMA entry, including diagonal, to the constant `z = exp(i(Ωτ−ωτ))`, and initialize the queue with θ₋d,…,θ₀. Every delayed input equals z, every EMA entry remains z, and every off-diagonal reported R is 1. The phase update has coupling −K sin(Ωτ), so it advances by dt·Ω. It remains to select b so the weight update fixes it:

- **Interior branch:** `b=η/γ`, provided `mb<C` (strict capacity slack). Clipping and projection do not act.
- **Projected branch:** let `t=1−dtγ>0`, `h=dtη>0`, and ε=`scale_epsilon`>0. Choose the unique positive root of
  `m t b² + (m h + ε − C t)b − C h = 0`.
  If `m(tb+h)>C`, the engine's strict pre-violation test selects projection, and `b=C(tb+h)/(m(tb+h)+ε)` exactly. This uses **one** factor from `minimum.outer`, not its square. The condition must be checked; the quadratic alone does not establish which branch executes. The root has mb<C because ε>0. Apply the separate Kτ<1 condition for uniqueness of Ω.

Initializing the *entire delay history and EMA* on this orbit is essential to this exact construction. The engine's ordinary initializer instead uses random phases, replicated history and zero coherence. No claim is made that it reaches this orbit, or that the orbit is stable, or that the heterogeneous production frequencies satisfy the assumptions. The fixed phases rotate; they do not freeze. Ω need not equal ω.

## Checks on the actual Python engine

`test_rotating_solution.py` constructs initial states and calls `advance_state` 1,000 times per case, N=12, d=50, dt=.01, τ=.5, homogeneous ω≈1.42833. Both use μ=.03, γ=.015, T_window=17.5, C=(1−.05)/1.5; projected case uses η=.04, interior case η=.0005. The latter is deliberately non-production. Initializations are hand-built on the orbit, not the standard initializer.

| Branch | b | Ω | Projection steps | max circular phase error |
|---|---:|---:|---:|---:|
| Interior | 0.0333333333333 | 1.21850642724 | 0/1000 | 6.39e−14 |
| Projected | 0.0575757575757 | 1.09787260109 | 1000/1000 | 8.97e−14 |

Maximum errors in B, complex C, and reported R are also in `test.log`. A negative control that assumes Ω=ω produces a one-step phase-increment error ≈0.00415. Float64 numerical agreements are evidence for these cases only, not an exact-real proof or Python–Lean equivalence.

## Reproduce and provenance

```sh
python3 /home/user/AIEFS_cycle8/test_rotating_solution.py
```

Requires NumPy, `AIEFS_cycle7/symmetric_reduction_test.py` and `AIEFS/aief_experiment_engine_v1.py` (hashes in `SHA256SUMS.txt`). Engine bytes match main `871417d58504dd2e42276bde8142e3fdac73df44`. Since last cycle, PR #38 landed a C014 follow-up; this cycle did not audit it. No Lean build, full project gate, full mutation suite, or independent review occurred. GitHub connector was previously reported unsupported; no push attempted. Prior inbox drafts remain unverified.
