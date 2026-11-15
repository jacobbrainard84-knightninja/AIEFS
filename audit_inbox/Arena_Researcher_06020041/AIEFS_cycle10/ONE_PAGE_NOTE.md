# Cycle 10 — transverse stability and a projection kink

**Status:** analytic argument plus full-engine numerical Jacobian checks, not Lean-formalized or independently reviewed. These results concern the specially prepared homogeneous-frequency orbit from Cycle 8, not generic production trajectories.

## Interior orbit: extend stability beyond symmetric perturbations

Take a Cycle 8 **interior** orbit with N≥2, d≥1, homogeneous ω, positive uniform off-diagonal b=η/γ, strict capacity slack `(N−1)b<C`, no shuffle, and α∈(0,1), 0<dt·γ<1. Put `h=dt·b·cos(Ωτ)`. If **0<(N−1)h<1**, the orbit is locally exponentially attracting modulo common phase shift in the full state space with arbitrary node-dependent phase/history and complex-EMA perturbations and arbitrary symmetric zero-diagonal weight perturbations. This is a proposed analytic consequence of a smooth quotient-map linearization, not a Lean theorem; no explicit basin is given. Frequencies remain identical and fixed.

In the rotating frame, write EMA perturbations relative to z as `uᵢⱼ+i vᵢⱼ`. Their linearized real parts obey `u⁺=αu`; weights obey `δB⁺ᵢⱼ=(1−dtγ)δBᵢⱼ+dt(η+μ)α(uᵢⱼ+uⱼᵢ)/2`; phase perturbations depend on the new weight row sums; imaginary EMA perturbations depend on current/delayed phase differences. Thus, after ordering variables, the Jacobian is block triangular: real EMA, weights, phases, imaginary EMA. The two EMA blocks have eigenvalue α, and weights have eigenvalue 1−dtγ.

The phase block decomposes into one common mode and N−1 zero-sum modes, with polynomials

`P(λ)=λ^(d+1)−(1−m h)λ^d−m h`,
`Q(λ)=λ^(d+1)−(1−m h)λ^d+h`, where m=N−1.

As in Cycle 9, P has only a simple λ=1 on the unit circle. For Q, if |λ|≥1 then `|λ|≤1−m h+h`; this is <1 for m>1. For m=1, equality would force both λ=1 and λ^(−d)=−1, a contradiction. Hence every transverse root is strictly inside the disk. After quotienting the one common-phase neutral direction, standard discrete local stability gives the claimed restricted-parameter orbital stability. This does not cover heterogeneous ω, projected orbits, non-symmetric weight state, shuffle, or convergence from the usual random initial conditions.

## Projected orbit: do not reuse a smooth full-network Jacobian

At the projected orbit, all row sums tie. The engine uses `np.minimum.outer(scale,scale)` (engine lines 808–817), so the full map is **not differentiable** there in general even though its restriction to the symmetric subspace is smooth. For N=3, perturb only edge (0,1) of B by t. In the strictly active projection branch, the one-sided derivative of output edge (0,2) is nonzero for t>0 and zero for t<0. Specifically it is `−(1−dtγ) β C/(2β+ε)²` from the positive side, where β is the common pre-projection weight and ε is `scale_epsilon`. This invalidates a naive full-network smooth-linearization argument at the tie; it **does not prove instability**. Cycle 9's symmetric-subspace result remains limited to that subspace.

## Evidence and limits

Run `OPENBLAS_NUM_THREADS=1 python3 /home/user/AIEFS_cycle10/full_network_check.py`. For synthetic N=3 interior orbits, central differences of the **actual engine** agree with the derived full Jacobian to 4.96e−11 at d=3 and 3.04e−10 at d=50; each has one neutral eigenvalue and numerical non-neutral spectral radius 0.99985. Projected N=3, d=50 gives one-sided weight-derivative discrepancies tending to 0.499369 as h shrinks from 1e−5 to 1e−7. Those finite positive perturbations exceed the projected orbit's tiny ~1e−12 capacity slack and are not valid feasible initial states; the exact symbolic one-sided argument applies to sufficiently smaller feasible perturbations because the orbit has strictly positive slack and strictly active pre-projection. The engine map was evaluated without validating those perturbed inputs. These checks are not a proof, do not cover the production N=12/heterogeneous ω system, and do not establish full projected stability.

Tested engine SHA-256 `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede` matches main `871417d58504dd2e42276bde8142e3fdac73df44`, rechecked this cycle. Script/helper hashes and output: `SHA256SUMS.txt`, `test.log`. No Lean build, full project gate, mutation suite, independent review, push, or claim promotion.
