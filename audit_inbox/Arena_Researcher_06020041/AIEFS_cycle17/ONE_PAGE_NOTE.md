# Cycle 17 — all eigenvalues and a simple neutral mode for the proposed phase block

**Status: analytical candidate, not a new Lean theorem or independent review.** This closes the *linear algebra gap on the proposed block* identified in Cycle 16. It does not identify that block with the engine Jacobian or establish nonlinear/production stability.

Let N≥2, d≥0, 0<h and (N−1)h<1; put m=N−1 and a=1−mh. On C^((d+1)N), define T by head `a x₀ + h(J−I)x_d` and shifts `x⁺_k=x_(k−1)` for 1≤k≤d; J is the all-ones matrix. Define

`C(z)=z^(d+1)−a z^d−mh`, `P(z)=z^(d+1)−a z^d+h`.

**Claim (exact linear block):** `det(zI−T) = C(z) P(z)^(N−1)`. Consequently every eigenvalue has modulus at most one; 1 is the only possible unit-circle eigenvalue and is algebraically simple. Its eigenspace consists of vectors constant across *both* nodes and history slices. Every other eigenvalue is strictly inside the unit disk. Thus powers of T converge exponentially to the spectral projection onto that neutral eigenspace. This is a conclusion about T, not the engine.

**Argument.** The node space splits as span(1) ⊕ {v: sum(v)=0}; this is an invariant direct sum on every history slice. J−I acts as multiplication by m on the first part and −1 on the second. A scalar delay companion block with feedback b has characteristic polynomial `z^(d+1)−a z^d−b`. This follows, for z≠0, by eliminating shift coordinates in `zI−T` (the shift block has determinant z^d); the resulting polynomial identity extends to z=0. For d=0 the matrix is simply `a+b` and the same formula holds. Applying this once with b=mh and N−1 times with b=−h gives the factorization, without assuming individual eigenvectors are already common or transverse.

Main's `DelayRoots.lean` proves the needed common and transverse root bounds under these hypotheses, including N=2. In addition `C(1)=0`, `C′(1)=1+d mh>0` (also valid at d=0), while `P(1)=Nh>0`. Therefore the factorization makes 1 an algebraically simple root. At z=1, the shift equations make every history slice equal and the head equation gives `h(J−NI)y=0`, so y is constant. Finite-dimensional Jordan theory then gives exponential convergence after removal of the simple neutral mode; the exponential rate is not quantified.

**Checks and limits.** `python check_factorization.py` (Python 3, SymPy 1.14.0) passed 16 exact symbolic characteristic-polynomial checks, N=2,…,5 and d=0,…,3 at h=1/(2N), and checked neutral nullity. A deliberately included self-loop failed the specified factorization. At N=2,d=1,h=1 the strict condition fails and P=z²+1 has unit-circle roots ±i. These are finite checks, not a formal or independent proof. The decomposition, determinant, multiplicity and convergence arguments are **not Lean-verified**; Cycle 16's Lean results concern only modes under explicit slice assumptions. Projected gate, EMA and weight couplings, homogeneous-orbit engine identification, full nonlinear stability, and heterogeneous cases remain open.

Main was rechecked at `d2a62b7f9e6456ade8591d5f12c9ccdeed185d19` and inbox at `2e63035c1c973ff07e8124e3ca9b8e198b4e5171`; its `DelayRoots.lean` is byte-identical to Cycle 16's main version. This cycle did not run a Lean build or the full project gate. No push or claim promotion.
