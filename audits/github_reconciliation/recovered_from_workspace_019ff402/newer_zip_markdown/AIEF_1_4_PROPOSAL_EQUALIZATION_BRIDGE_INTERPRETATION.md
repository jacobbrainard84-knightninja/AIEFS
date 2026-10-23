# AIEF-1.4 proposal-equalization bridge: interpretation note

**Status:** interpretation of the user-supplied replay report  
**Date:** 2026-07-27  
**Replay:** production run `5a9f093a2fe0`, exceptional seed `4619122171158768524`  
**Hash caveat:** the generated output files were not present in this workspace when this note was written; numerical values below are transcribed from the supplied report and are not a substitute for its `analysis_manifest.json`.

## 1. Gate result

The proposal-equalization audit passes its intended structural gate.

- Final replay is exact.
- All proposal, projection, recurrence, radial, magnitude-quotient, and symmetrization identities close at approximately \(10^{-16}\).
- Positive selected proposal support, clipped controller rows, the global gate, the isolated K3 row sums, and winner map \((7,2,7)\) persist across all 32,000 transitions.
- Both proposal channels acquire the EMA-rate envelope late.
- Both directed alignment residuals decay faster than the EMA envelope over the saved late windows.
- Directed magnitude denominators remain far from zero.

These are finite-horizon facts from one replay, not independent seed-level replications or infinite-time limits.

---

## 2. Exact implementation closure

Maximum errors reported across the two channels are:

\[
\begin{array}{c|c}
\text{identity}&\text{maximum error across channels}\\ \hline
\text{proposal difference}&5.56\times10^{-17}\\
\text{projected weight difference}&1.32\times10^{-16}\\
\text{proposal recurrence}&1.64\times10^{-16}\\
\text{symmetrized }R&3.89\times10^{-16}\\
\text{directed radial recurrence}&7.29\times10^{-16}\\
\text{magnitude quotient}&8.33\times10^{-17}
\end{array}
\]

Thus the downstream recurrences are numerically exact to floating-point precision on the replay:

\[
d_{n+1}^j=\lambda_n^j d_n^j+dt(\eta+\mu)r_{n+1}^j,
\qquad j\in\{\mathrm L,\mathrm R\}.
\]

This establishes implementation correctness, not asymptotic forcing decay.

---

## 3. Two channels with sharply different internal memory

The EMA multiplier and rate are

\[
\alpha=0.999428829846,
\qquad
r_{\rm EMA}=-dt^{-1}\log\alpha
\approx0.0571333334.
\]

### Fixed-left channel \((25,59)\)

Late median branch multiplier:

\[
\lambda_{\mathrm L}\approx0.998738246680,
\]

with intrinsic filter rate

\[
r_{\mathrm L}
=-dt^{-1}\log\lambda_{\mathrm L}
\approx0.1262550001.
\]

The gap is

\[
\boxed{
r_{\mathrm L}-r_{\rm EMA}
\approx0.0691216667,}
\]

which closes the previously observed operational-memory value

\[
\kappa\approx0.06913.
\]

Even the maximum saved multiplier satisfies

\[
\max_n\lambda_n^{\mathrm L}
=0.999018123051
<\alpha.
\]

Thus throughout the saved record the fixed-left proposal filter is faster than the EMA forcing.

### Right-mode channel \((59,29)\)

Late median branch multiplier:

\[
\lambda_{\mathrm R}\approx0.499369154879,
\]

with intrinsic filter rate

\[
r_{\mathrm R}\approx69.4409667.
\]

Its saved maximum is only

\[
\max_n\lambda_n^{\mathrm R}=0.668129340534<\alpha.
\]

The right channel is therefore almost memoryless on the EMA timescale. Its late proposal difference is slaved to the fresh resonance difference rather than maintained by its homogeneous weight memory. This explains why right invariance is reached much earlier than fixed-left closure.

---

## 4. Late rate closure

Over \([250,320)\), the report gives

\[
\begin{array}{c|cc}
\text{channel}&r_{\Delta x}&r_{\Delta R}\\ \hline
\text{fixed-left}&0.0571332&0.0571333\\
\text{right-mode}&0.0571338&0.0571324
\end{array}
\]

against

\[
r_{\rm EMA}=0.0571333334.
\]

All corresponding late \(R^2\) values are reported as one to displayed precision. Since both homogeneous proposal filters are faster than \(\alpha\), this is a nonresonant forcing-dominated transfer:

\[
\Delta R\text{ at rate }r_{\rm EMA}
\Longrightarrow
\Delta x\text{ at rate }r_{\rm EMA}.
\]

This proposal-layer result should not be conflated with the Jordan-type resonance in the complex EMA tracking subsystem.

---

## 5. Alignment residuals are upstream and faster

Over \([250,320)\), directed alignment-residual rates are approximately

\[
\begin{array}{c|cc}
\text{channel}&\text{forward}&\text{reverse}\\ \hline
\text{fixed-left}&0.108106&0.108483\\
\text{right-mode}&0.106136&0.106140
\end{array}
\]

and therefore exceed \(r_{\rm EMA}\) by roughly \(0.049\)–\(0.051\). The directed squared-magnitude recurrence

\[
\Delta M_{n+1}
=\alpha\Delta M_n
+\alpha(1-\alpha)e_n
\]

is consequently consistent with an asymptotically homogeneous \(\alpha\)-mode over the saved late window: the alignment forcing \(e_n\) decays faster than the radial memory term.

The rates are near, but not equal to, twice the EMA rate. No exact \(2r_{\rm EMA}\) law should be claimed from the finite report.

Magnitude denominators remain well conditioned:

\[
\min(|C_a|+|C_b|)
\ge1.73473
\]

for the fixed-left channel and at least \(1.47003\) for the right-mode channel over the first interval, approaching \(2\) late. Thus the magnitude quotient does not amplify a vanishing-denominator singularity.

---

## 6. Branch cone and limiting tie

The minimum saved winner margin is

\[
4.44\times10^{-14}.
\]

This is not evidence of a uniformly separated strict branch. It is evidence that the replay approaches its tie boundary while remaining on the same side at every saved finite step.

On the isolated equal-capacity K3,

\[
q_7-q_2=x_{59}-x_{29}=d^{\mathrm R},
\]

\[
q_2-q_{11}=x_{25}-x_{59}=d^{\mathrm L}.
\]

The winner map \((7,2,7)\) is equivalent to

\[
d^{\mathrm L}>0,
\qquad
d^{\mathrm R}>0.
\]

Proposal equalization therefore approaches the corner

\[
d^{\mathrm L}=d^{\mathrm R}=0
\]

from the positive branch cone.

At exact equality, all three node scales tie and the full K3 controller matrix is

\[
C_{K_3}
=
\begin{pmatrix}
1&1&0\\
1&0&1\\
0&1&1
\end{pmatrix},
\qquad
\ker C_{K_3}=\{0\}.
\]

Hence the nonzero mode \(v\) is an exact carrier on every strict partial-controller state, but not a nonzero two-sided controller-fiber mode of the exact triple-tie stratum. The correct limiting object is the one-sided selected branch-matrix limit. The exact tied map remains directionally nonsmooth.

This distinction is forced by the new branch-margin result and should be retained in all manuscript statements.

### Saved sign audit

The additional trajectory extraction reports

\[
\begin{array}{c|cc|cc}
&\min\Delta x&\min\Delta R&\text{sign changes}&\text{all positive}\\ \hline
\text{fixed-left}&5.42267\times10^{-9}&5.35277\times10^{-9}&0&\text{yes}\\
\text{right-mode}&2.81997\times10^{-14}&2.01542\times10^{-11}&0&\text{yes}
\end{array}
\]

Thus the saved trajectory approaches the tie boundary inside the positive proposal and resonance cones. Because

\[
d_{n+1}^j=\lambda_n^jd_n^j+a_Rr_{n+1}^j
\]

with \(\lambda_n^j,a_R>0\), positivity of \(r_{n+1}^j\) is a sufficient inductive barrier against a finite winner crossing. The future proof target can therefore be sharpened to one-sided resonance ordering:

\[
R_{25,n}>R_{59,n}>R_{29,n}
\]

for every finite step, with both differences tending to zero.

The final right-mode proposal difference is already near floating-point resolution. Its fitted tail and winner label should therefore be treated as deterministic finite-replay facts, not evidence of a numerically robust positive margin.

### Asymptotic transfer-gain check

If \(r_{n+1}/r_n\to\alpha\) and \(\lambda_n\to\lambda_*<\alpha\), the exact recurrence implies

\[
\frac{d_n}{r_n}
\to
G_*
=
\frac{dt(\eta+\mu)\alpha}{\alpha-\lambda_*}.
\]

Using \(dt(\eta+\mu)=0.0007\):

\[
\begin{array}{c|cc}
\text{channel}&G_*\text{ predicted}&(\Delta x/\Delta R)\text{ final}\\ \hline
\text{fixed-left}&1.0130571021&1.0130571619\\
\text{right-mode}&0.0013990334&0.0014019490
\end{array}
\]

The fixed-left relative discrepancy is approximately \(5.9\times10^{-8}\). The right-mode discrepancy is approximately \(2.1\times10^{-3}\), consistent with that channel already operating near the numerical floor. This supplies a parameter-free amplitude closure in addition to the rate closure.

---

## 7. Updated evidence hierarchy

### Exact implementation identities

- both proposal difference formulas;
- both projection coefficients;
- both forced proposal recurrences;
- both directed radial recurrences;
- both magnitude quotients;
- symmetrized resonance reconstruction;
- branch-cone identities.

### Saved finite-replay facts

- exact replay;
- all branch assumptions hold over 32,000 transitions;
- both \(\Delta R\) and \(\Delta x\) channels acquire the EMA rate late;
- alignment residuals decay faster over every reported interval;
- no magnitude denominator degeneracy;
- strict winner margins shrink to near machine resolution without a recorded crossing.

### Conditional theorem now supported on the finite record

\[
\text{alignment decay}
\Longrightarrow
\text{resonance equalization}
\Longrightarrow
\text{proposal equalization}
\Longrightarrow
\text{one-sided branch-matrix closure}.
\]

### Still open

- continuation of alignment-residual decay beyond \(t=320\);
- proof that \(d_n^{\mathrm L},d_n^{\mathrm R}>0\) for every finite future step while both tend to zero;
- derivation of the alignment limits from delayed phase/history dynamics;
- a directional theorem describing the exact triple-tie map and its one-sided cones;
- generality across other branches and seeds.

---

## 8. Next theorem target

The next structural target is no longer proposal equalization itself. The downstream implication has been closed conditionally and validated on both channels.

The remaining target is a **two-channel alignment theorem**:

> Under the coupled delayed phase/EMA dynamics, prove that the directed alignment residuals for both edge pairs \((25,59)\) and \((59,29)\) tend to zero while the proposal differences remain in the positive branch cone.

A complete trajectory theorem must combine:

1. one-sided branch-cone invariance;
2. directed alignment-residual convergence;
3. the already proved stable radial and proposal filters;
4. one-sided convergence of selected branch matrices to the fixed analytic family.
