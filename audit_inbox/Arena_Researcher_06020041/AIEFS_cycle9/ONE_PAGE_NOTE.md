# Cycle 9 — local stability inside the synchronized subspace

**Status:** conditional analytic argument and numerical checks, not Lean-formalized or independently reviewed. This addresses stability of Cycle 8's rotating orbit only under perturbations that preserve its full permutation symmetry. It does **not** establish stability to node-asymmetric perturbations or generic attraction in the full network.

## Claim and conditions

Take either Cycle 8 orbit with d≥1; let `K=(N−1)b`, `a=dt·K·cos(Ωτ)`, τ=d·dt, and assume:

- `0<a<1`, `0<α<1`, and `0<dt·γ<1`;
- the orbit lies strictly inside its chosen clipping/projection branch: β>0 and either `(N−1)β<C` (interior) or `(N−1)β>C` (projected), where β=b+dt(η−γb), C=capacity;
- nearby perturbations stay in the symmetric subspace: common phase histories, a common complex accumulator entry and uniform off-diagonal weights. Diagonal weights are zero; no shuffle.

Then, for the exact-real scalar recurrence from Cycle 7, the rotating orbit is **locally exponentially attracting modulo a constant common phase shift** within that subspace. In particular the complex coherence and weights return locally to their orbit values. No explicit neighborhood or rate constant is established. The result uses the standard discrete-time local linearization theorem on the quotient by common phase; it is an analytic argument, not a kernel-checked theorem.

## Calculation

Write co-rotating phase deviations as xₙ,…,xₙ₋d, let the complex EMA perturbation relative to the unit phasor be u+iv, and let y be the weight perturbation. To first order, `u⁺=αu`, `v⁺=αv+(1−α)(xₙ−xₙ₋d)`, and

`y⁺ = g′[(1−dtγ)y + dt(η+μ)αu]`,
`xₙ₊₁ = (1−a)xₙ + a xₙ₋d − dt·(N−1)sin(Ωτ)y⁺`.

The remaining phase-history entries shift. Here g′=1 in the interior; in the projected branch `g′=C ε/((N−1)β+ε)²`, ε=`scale_epsilon`. The eigenvalues are two copies of α, the weight eigenvalue `g′(1−dtγ)`, and the roots of

**P(λ)=λ^(d+1)−(1−a)λ^d−a.**

For `0<a<1`, λ=1 is simple (`P′(1)=1+ad>0`), and all other phase roots have modulus <1. To see this, for any nonzero root with |λ|≥1, the equation `λ=(1−a)+aλ^(−d)` implies |λ|≤1; equality in the triangle inequality forces λ=1. In the projected branch `0<g′<1/4` under the strict projection condition, so the weight eigenvalue is also inside the unit disk; interior g′=1 and `0<dtγ<1`. The unique unit eigenvalue is common phase translation. The quotient Jacobian is therefore strictly Schur stable; smoothness follows from staying strictly within a branch and nonzero EMA norm. Standard local stability then yields local exponential attraction on the quotient, and summable phase-increment deviations yield a limiting common phase shift.

The positive-a condition is sufficient, not necessary: a tested `d=3, a=−0.1` also had spectral radius 1, whereas `d=3, a=−0.5` had an unstable root ≈1.23375. Do not infer instability for every negative a.

## Evidence and reproducibility

`python3 /home/user/AIEFS_cycle9/stability_check.py` passed four tests. On the two Cycle 8 examples, analytic Jacobians agreed with central differences to 8.39e−12 (interior) and 7.03e−12 (projected); non-neutral spectral radii were 0.99985 and 0.999428735. One small symmetric perturbation per case, evolved for 40,000 steps in the **scalar transcription**, reduced the reported quotient norm by factors 0.000561 and 1.74e−9. These finite examples are not a proof of the theorem or checks of the full network. The first negative-control attempt mistakenly expected a=−0.1 to be unstable; its failed test is retained in `initial_negative_control_failure.log` and the corrected control uses −0.5.

The script requires the Cycle 8 and Cycle 7 helpers and the workspace engine; hashes are in `SHA256SUMS.txt`. Main remained `871417d58504dd2e42276bde8142e3fdac73df44` at the start of this cycle. No Lean build, full project gate, mutation suite, independent review, push, or claim promotion occurred.
