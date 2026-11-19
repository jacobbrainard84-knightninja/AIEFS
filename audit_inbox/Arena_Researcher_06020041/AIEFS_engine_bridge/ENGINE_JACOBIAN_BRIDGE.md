# Proposed bridge: engine step to the complete-graph phase-history block

**Status: written, exact-real derivation for review; not Lean-checked, not a formal Python semantics theorem, and not an independent audit.** This is deliberately a bridge statement, not another layer depending on the unmerged Lean stack. The source is `aief_experiment_engine_v1.py` at main `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19`; its SHA-256 is `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`. Local source bytes were compared with that commit. Line references below refer to that version.

## 1. Proposed precise statement and assumptions

Consider an exact-real, no-shuffle idealization of the engine step, with complex EMA and angles on the circle, using the operation order cited below. Let N≥2, `dt>0`, integer d≥1, `τ=d dt`, and all natural frequencies equal ω. Let γ>0, η>0, μ≥0, and let the positive capacity parameter in the engine be `C=(a−δ)/q_cap`, where `q_cap>0`. Put `m=N−1`, `b=η/γ`, and suppose `m b<C`. Choose any real solution Ω of

`Ω=ω−m b sin(Ωτ)`.

For each integer t, use the prepared orbit with common unwrapped angle `θ̄_t=θ₀+t dt Ω`, weights `B̄ᵢⱼ=b` off diagonal and zero on the diagonal, and complex accumulator `Z̄ᵢⱼ=z=exp(i(Ωτ−ωτ))` for every i,j. The queue is the complete sequence `θ̄_(t−d),…,θ̄_t` modulo 2π; the separately stored `theta` equals its last entry. Use `shuffle_driver=False` and the engine's `α=exp(−dt/T_window)` for positive `T_window`.

**Claim to formalize:** in local circle charts, the Fréchet derivative of this exact-real step at the prepared orbit, restricted to the consistent-history state and represented by `(x₀,…,x_d,u,v,w)` below, has the explicit form in §3. In particular, on the invariant set `u=w=0` (with arbitrary v), its phase-history output is precisely the proposed no-self-loop complete-graph shift block in §4. The derivative formula itself does **not** require `0<m h<1`; that additional hypothesis is needed only for the previously proved root bounds.

This statement treats the engine's NumPy operations as a smooth exact-real idealization where the indicated branch is locally fixed. Literal IEEE floating-point execution is a discrete computation, not the same Fréchet-differentiable map; no proof of floating-point equivalence is claimed. The engine's routine state validator checks dimensions and length, but does not assert that `theta` equals the last history entry ([lines 613–643](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/d2a62b7f9e6456ade8591d5f12c9ccdeed185d19/aief_experiment_engine_v1.py#L613-L643)); that consistency is an **additional hypothesis**, not a consequence of validation.

## 2. Why the prepared orbit is on the smooth interior branch

At the orbit, `theta_i−delayed_j−ωτ=Ωτ−ωτ`, so the instantaneous coherence and accumulator are both z, with |z|=1. Consequently the symmetrized off-diagonal magnitude is 1. The EMA update and symmetrization occur at [lines 729–750](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/d2a62b7f9e6456ade8591d5f12c9ccdeed185d19/aief_experiment_engine_v1.py#L729-L750). In the weight update, `(η+μ)·1−μ−γb=η−γb=0`, hence the off-diagonal pre-clipping weight is b. Since b>0, off-diagonal clipping is locally inactive. The code then symmetrizes and clears the diagonal ([lines 789–797](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/d2a62b7f9e6456ade8591d5f12c9ccdeed185d19/aief_experiment_engine_v1.py#L789-L797)); diagonal clipping need not be differentiable because the diagonal is subsequently discarded and does not enter the phase coupling.

The post-symmetrization row sum is m b<C, so `a−q_cap m b>δ`: the pre-violation predicate is false with strict slack and remains false nearby by continuity ([lines 802–813](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/d2a62b7f9e6456ade8591d5f12c9ccdeed185d19/aief_experiment_engine_v1.py#L802-L813)). Thus projection is locally inactive; the diagnostic threshold `projection_active` is not substituted for this strict branch condition. The phase coupling on the orbit is `−m b sin(Ωτ)`, yielding the stated Ω equation ([lines 830–839](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/d2a62b7f9e6456ade8591d5f12c9ccdeed185d19/aief_experiment_engine_v1.py#L830-L839)). Existence of at least one Ω follows by continuity from the signs at `ω−m b` and `ω+m b`; uniqueness would require an additional condition and is not needed here.

## 3. Derivative calculation

Take x_k(i) as the real perturbation of the phase at time t−k, for k=0,…,d, in a consistent local lift. Write the complex accumulator perturbation as `δZᵢⱼ=z(uᵢⱼ+i vᵢⱼ)` with real u,v, and write `wᵢⱼ=δBᵢⱼ`. Set

`ρ=1−dt γ`, `κ=dt(η+μ)`, `h=dt b cos(Ωτ)`, `g=dt sin(Ωτ)`.

For an array A let `sym₀(A)ᵢⱼ=(Aᵢⱼ+Aⱼᵢ)/2` off diagonal and 0 on the diagonal. If the physical tangent is restricted to symmetric zero-diagonal weights, `sym₀(w)=w`. More generally the next-weight derivative uses `sym₀(w)` because the engine explicitly symmetrizes.

1. **EMA and magnitude.** Differentiating the instantaneous exponential at z gives `δz_inst=z i(x₀(i)−x_d(j))`. Therefore
   `u⁺ᵢⱼ=αuᵢⱼ`,
   `v⁺ᵢⱼ=αvᵢⱼ+(1−α)(x₀(i)−x_d(j))`.
   Since |z|=1, `D|·|_z(z(u+iv))=u`; the driver coherence perturbation is `α sym₀(u)` when shuffle is off. This includes the EMA update **before** taking magnitude, matching lines 742–750.
2. **Weight.** With positive off-diagonal pre-clipping entries and no projection,
   `w⁺=ρ sym₀(w)+κ α sym₀(u)`.
   There is one symmetrization, not a squared endpoint scale. Any diagonal entries of the raw perturbation are irrelevant after diagonal erasure.
3. **Phase.** Differentiate the sine at `−Ωτ`, and use **new** weights, as the source does at lines 823 and 830–835:
   `x⁺₀(i)=(1−m h)x₀(i)+h∑_{j≠i}x_d(j)−g∑_{j≠i}w⁺ᵢⱼ`.
   The phase-independent natural-frequency term has zero derivative because ω is fixed, not perturbed.
4. **History.** The append and drop at [lines 841–844](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/d2a62b7f9e6456ade8591d5f12c9ccdeed185d19/aief_experiment_engine_v1.py#L841-L844) give `x⁺_k(i)=x_(k−1)(i)` for k=1,…,d. The queue is ordered oldest-first in Python but indexed newest-first in this derivation.

The modulus is differentiable here because z≠0. The exact complex accumulator may be perturbed in an open ambient space for the derivative; some such perturbations are not physically reachable from the standard EMA initializer. A derivative in this ambient extension should not be confused with a feasible-trajectory experiment.

## 4. Exact bridge target and remaining proof obligations

When u=w=0, their derivative updates remain zero. The phase evolution is independent of v, though v is generally driven by x, so **the phase block is a factor of this invariant subsystem**, not necessarily an invariant subspace obtained by additionally setting v=0. Its head and history are

`x⁺₀(i)=(1−m h)x₀(i)+h[(∑ⱼ x_d(j))−x_d(i)]`,
`x⁺_k(i)=x_(k−1)(i)` for 1≤k≤d.

This is the real version of the earlier proposed complexified complete-graph phase block; complexification is a further mathematical step. To turn this note into a checked engine result, a reviewer/formalizer must establish:

- a precise exact-real state type and a relation to the Python state, including history ordering, consistent `theta`, and local circle charts (especially at a numeric modulo cut);
- the invariant prepared orbit and strict off-diagonal clipping / pre-projection margins;
- Fréchet derivative rules for complex exponential, magnitude at nonzero z, symmetrization, the weight update, sine and queue shift, in the exact source order;
- the matrix/block identification and only then, separately, application of the root and simplicity results. A full-system stability theorem additionally needs the EMA/weight blocks and a justified neutral-mode quotient.

Nothing here covers the active projection branch, a non-differentiable gate tie, shuffle, heterogeneous ω, or attraction from ordinary random initialization. The source-based derivation was not independently reviewed, formalized, or re-executed in this work. Previous numerical finite differences are separate evidence and are not required to read or check this derivation. No mutation suite, project gate, push or promotion was performed.
