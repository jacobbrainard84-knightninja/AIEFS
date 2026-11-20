# Researcher 040282 — Cycle 004: complex EMA, reported coherence, and drive bounds

- **Agent:** Researcher 040282, Arena.ai research agent.
- **Date:** 2026-09-04, Atlantic/Reykjavik (UTC).
- **Status:** local, self-red-teamed research input. Independent-seat review, owner upload, publication, and integration are unconfirmed. No remote changes or bot contact occurred.
- **Current-source basis:** `main` at `ad58a46ae8da79c19b5484762363eb2e9f2f7923`. A read-only refresh acquired 27 selected files, including all 14 active-project Lean files and five historical Lean fixtures. Eight intake/navigation files were checked at `5c1ffed0377c4769154e9342464ce7265cf1c599`. No existing EMA formalization or 040282 feedback was found in those selected sources. This is not a complete branch/assignment audit.
- **Suggested intake filename:** `audit_inbox/2026-09-04_researcher040282_004_complex-ema.md`.

## 1. What this adds

**The library now has a candidate exact-real component matching the source's directed complex EMA and its actual reported coherence, not a cosine substitute.** The component is connected to the previous positive-drive-row and gate-floor definitions.

The important results are:

1. The source phase input has unit complex norm. The EMA preserves the unit disk for any supplied phase sequence and `0≤alpha≤1`.
2. The reported R is symmetric, nonnegative and zero-diagonal, and is at most one under that invariant. These properties do **not** require a symmetric or zero-diagonal complex accumulator.
3. The exact difference recurrence retains the input-forcing term. Homogeneous geometric forgetting is proved only for **identical entire prescribed input sequences**. A bound is also proved for the difference in reported observables.
4. The fixed-input closed form and conditional convergence are proved. Zero-start constant unit input gives `|C_n|=1-alpha^n`, regardless of its phase angle.
5. The actual reported-coherence expression yields normalized-drive bounds and the finite positive-row bound `(N-1)*eta/gamma`. A compiled theorem feeds this into the prior applied-factor lower floor after a source-shaped coherence update.

The two new modules have **28 compiled declarations, including helpers**: 22 in `CoherenceEMA.lean` and six in `CoherenceDriveBridge.lean`. That count is not a claim of 28 new scientific discoveries. The new bridge also freshly recompiles 66 prior local declarations and five existing upstream scalar-core declarations; those **71 reused declarations are not new contributions or new authorship credit**. Accepted footprints use only `propext`, `Classical.choice`, and `Quot.sound`.

This supplies a missing EMA/coherence component, **not a complete delayed-system reference library, NumPy semantics proof, phase-locking theorem, or proof that actual future drive bands exist**. The previous per-edge OFF/ON results remain conditional on their bands. The new coarse range bound is not, by itself, a sharp ON certificate.

## 2. Exact component and source correspondence

Let I be an arbitrary index type; finiteness is needed only for row sums. Let C be a directed complex matrix, and theta, psi and omega real vectors. The delayed phase vector psi is an explicit input, corresponding to the source's `history[0]`:

\[
 \phi_{ij}=\theta_i-\psi_j-\frac{\omega_i+\omega_j}{2}\tau,
 \qquad z_{ij}=\exp(i\phi_{ij}),
\]
\[
 E_\alpha(C,z)=\alpha C+(1-\alpha)z,
 \qquad C^+_{ij}=E_\alpha(C_{ij},z_{ij}).
\]

The reported observable is

\[
 R(C)_{ij}=\begin{cases}
 0&i=j,\\
 (|C_{ij}|+|C_{ji}|)/2&i\ne j.
 \end{cases}
\]

The source-shaped component returns **`(Cnext, R(Cnext))`**. It does not return R of the previous accumulator, and it does not overwrite C with its symmetrized magnitude.

### Precise source points

In `aief_experiment_engine_v1.py` at the stated source basis:

- `:162–164`: `alpha=exp(-dt/T_window)`.
- `:224–228`: validation requires the computed binary alpha in `(0,1]`.
- `:707–708`: initialization sets the complex accumulator to zero.
- `:729–740`: the driver uses current phases, the **oldest** history vector, and the pairwise mean-omega/tau correction.
- `:743–745`: the EMA updates the complex accumulator **in place**.
- `:748–750`: the code takes magnitudes, averages forward/reverse magnitudes, and zeros only the returned R diagonal.

The mathematical component models those real/complex formulas. It does not yet formalize why a buffer contains a particular delayed state, phase wrapping/integration, or the complete `DynamicState` transition. Arbitrary real psi suffices for the norm theorem; that fact does not verify the source's history index. The finite source sensitivity test therefore separately checks that index.

**Index convention:** `C_0` is before any call, `C_{n+1}=E_alpha(C_n,z_n)`. After m actual `compute_R` calls, the source returns `R(C_m)` for `m≥1`. Thus a zero-start fixed-input formula after the first call is `1-alpha`, not zero. A call-number indexed at n=0 returns `R(C_{n+1})`.

## 3. Main proofs and their hypotheses

### 3.1 Unit disk and the actual readout

Lean proves `|exp(i*x)|=1` for the source-shaped real phase expression. It also proves the convex-norm bound

\[
 |E_\alpha(C,z)|\le\alpha|C|+(1-\alpha)|z|,
 \quad 0\le\alpha\le1.
\]

Consequently, if `|C_0|≤1` and every supplied input has norm at most one, the trajectory remains in the unit disk at every step. The actual phase input satisfies the input premise without a locking assumption. This holds pointwise for a matrix and any prescribed real phase/delayed vectors.

For any complex C, `R(C)≥0`, `R(C)` is symmetric and its diagonal is zero. If every entry has norm at most one, then `R(C)≤1`. No Hermitian/symmetry assumption on C, no zero complex diagonal, and no restriction on the phase offsets are needed.

The report also proves the reverse-triangle observable bound

\[
 |R(C)_{ij}-R(D)_{ij}|
 \le\frac{|C_{ij}-D_{ij}|+|C_{ji}-D_{ji}|}{2}.
\]

It includes the diagonal case, where the left side is zero.

For exact real `dt,Tw>0`, `alpha=exp(-dt/Tw)` lies strictly in `(0,1)`. This is **not** a theorem that a binary64 implementation always returns a strict interior value; see §6.

### 3.2 Forced differences, not unconditional homogeneous decay

For arbitrary real alpha and arbitrary complex values, the compiled identity is

\[
 E_\alpha(C,z)-E_\alpha(D,w)
 =\alpha(C-D)+(1-\alpha)(z-w).
\]

The input-forcing term cannot be omitted for two general coupled runs. This respects the existing registry S11 qualification; it does not revive a retired unconditional decay claim.

For two component trajectories driven by the **same entire supplied sequence** z, Lean proves

\[
 C_n-D_n=\alpha^n(C_0-D_0).
\]

For `alpha≥0`, the norm equality is `|C_n-D_n|=alpha^n|C_0-D_0|`. Combining it with the readout inequality gives the matrix result

\[
 |R(C_n)_{ij}-R(D_n)_{ij}|
 \le\frac{\alpha^n}{2}
 (|C_{0,ij}-D_{0,ij}|+|C_{0,ji}-D_{0,ji}|).
\]

That is an **upper bound**, not an exact affine recurrence for magnitude differences. These identities do not require a fixed input, but do require equality of the inputs in the two sequences. Two different coupled states need not supply the same future inputs, even if their phases initially match.

### 3.3 Fixed input and interpretation of coherence

For constant complex z, the general algebraic closed form is

\[
 C_n=z+\alpha^n(C_0-z).
\]

The conditional convergence theorem assumes `0≤alpha<1` and proves `C_n→z`; it does not assert the source eventually produces constant z. From `C_0=0`, unit input `|z|=1`, and `0≤alpha≤1`,

\[
 |C_n|=1-\alpha^n.
\]

For a constant matrix of unit inputs, the compiled reported formula at each distinct node pair is likewise `R(C_n)_ij=1-alpha^n`; the reported diagonal remains zero.

Thus a fixed input at angle pi/2 or pi is not assigned cosine zero or minus one. Its limiting **magnitude** is one when `alpha<1`. This observable measures persistence of a complex phase relation, not closeness to zero phase offset. The statement is about the defined observable on supplied inputs, not stability or physical reachability of every clamped state.

At `alpha=1`, the component retains its initial accumulator. It does not forget it or converge to a different prescribed input. Strictness in the convergence hypothesis matters.

### 3.4 Drive rows and composition with the guarded map

Define

\[
 u_{ij}=\frac{(\eta+\mu)R(C)_{ij}-\mu}{\gamma}.
\]

For `eta,mu≥0`, `gamma>0`, and unit-disk C, the compiled bounds are

\[
 -\mu/\gamma\le u_{ij}\le\eta/\gamma.
\]

The drive is symmetric, but its diagonal is **`-mu/gamma`**, not zero. The previous library's `positiveDriveRow` masks the diagonal explicitly; the new bridge uses that actual definition rather than a shadow sum:

\[
 S_i(u)=\sum_{j\ne i}\max(0,u_{ij})
 \le D:= (\#I-1)\frac{\eta}{\gamma}.
\]

Here the degree is natural-number subtraction, including N=1. The positivity assumptions and nonzero gamma are not removed to cover gamma-zero forcing ablations.

After the source-shaped EMA update, this S bound holds for arbitrary phase vectors whenever the previous C is unit-disk and `alpha∈[0,1]`. For the previous proposal map, nonnegative/row-feasible B, `c≥0`, `eps>0`, and `0≤h≤1`, the compiled composition then proves

\[
 \min\left(1,\frac{c}{(1-h)c+hD+\varepsilon}\right)
 \le \lambda_{ij}(\mathrm{proposal}(h,B,u(C^+))).
\]

The formal conclusion uses the prior `edgeFloor c eps h D D` definition (the equal-endpoint maximum reduces to D). This bounds the **applied** factor on both global guard branches. It inherits the earlier correct zero-capacity behavior; strict positivity still requires `c>0`. The source specialization uses `h=gamma*dt` and the prior nonzero-gamma affine identity, not a new Python linkage theorem.

### Why this is not already an ON theorem

The global range bound can be too coarse. With ideal baseline constants, N=12 and maximal possible normalized drive `L=8/3`, its universal row bound is `D=88/3`. The exact Fraction calculation gives the corresponding comparison fixed point

`760000000/13200000003 < 3/25 = B_c`.

Therefore that coarse bound cannot issue the previous ON certificate here even at maximal L. This is **not** a claim that every edge is OFF: a conservative lower comparison failing to cross the threshold is not an upper/OFF proof. Sharper local row envelopes or another certificate are needed. The previous active K3 witness used the sharper endpoint row bound `16/3`, not this universal 12-node envelope.

## 4. Red-team design and exact finite evidence

The component, hypotheses, target uses, falsifiers, and source allowances were recorded before candidate proof/test execution. Initial compiler/import/elaboration failures were rejected; no recovery `sorryAx` or warning-bearing draft is accepted evidence. The successful final proof/control evidence appears in §9.

Eight mathematical wrong variants are attacked both through exact witnesses and deliberately false Lean payloads:

| Wrong variant | Exact witness / contradiction |
|---|---|
| Drop alpha upper bound | alpha=2,C=1,z=-1 gives next norm 3 |
| Drop alpha lower bound | alpha=-1,C=1,z=-1 gives next norm 3 |
| Drop input disk condition | alpha=1/2,C=0,z=4 gives next norm 2 |
| Drop equal-input premise | zero previous difference, inputs 1 and -1, alpha=1/2 give next difference 1 |
| Average complex directions before magnitude | C01=1,C10=-1: correct readout 1; norm of complex average 0 |
| Zero the complex diagonal | zero start, unit input, alpha=1/2: complex diagonal 1/2, reported diagonal 0 |
| Strict forgetting at alpha=1 | zero accumulator stays zero under constant input 1; error remains 1 |
| Replace coherence by cosine | constant complex state/input -1 has reported magnitude 1, not cos(pi)=-1 |

The first three Lean payloads assert a necessary real-part consequence of the false disk claim, with closed counterexamples whose norm/real part is computed exactly. This avoids mistaking a norm API/type-class failure for a mathematical rejection.

Separate trust controls test a proof hole, a new axiom, and missing declaration/axiom-print coverage. A proof hole/new axiom may raw-compile but must fail acceptance. The Python optimization control rejects `-O/-OO` before assertions can be bypassed.

The independent exact suite uses Gaussian-rational pairs and Fraction arithmetic, not NumPy or Lean evaluation:

- 64 shared-input pair cases and 64 fixed-input cases (including a zero-start path), with 16 updates per path;
- 2,176 unit-disk checks across the shared pair paths, 1,088 shared-difference checks, and 1,088 fixed-input closed-form checks, including initial states;
- alpha endpoints and near-endpoints; Pythagorean unit-circle inputs; nonzero/zero starts;
- 120 constructive finite matrix/readout/drive cases with N in `{1,2,3,6,12}`, zero eta/mu allowed and positive gamma; 327 endpoint row bounds are attained;
- exact witnesses for all eight wrong variants, and the coarse-envelope calculation above.

Seed `20260904`. These finite checks do not replace the universal Lean proof or establish coupled reachability.

## 5. Separate actual-source component experiment

Unlike the previous weight-step experiment, this one calls **actual `compute_R` without replacing it**. It compares both the updated complex C and the returned R with an independent scalar loop/cmath oracle, and checks in-place C identity, exact output symmetry/diagonal, and unchanged theta/B/history.

**Observed:** 34 valid controlled-state cases, **253 actual `compute_R` calls**, all passing. Maximum complex-state error was **0** in this experiment; maximum reported-R error was **`2.220446049250313e-16`**. The fixed allowance was absolute **`2e-14`**, relative zero; it was not enlarged after results.

The cases were:

- 30 two-call comparisons across N `{1,2,3,6,12}`, window ratios `{.5,1,2}`, and zero/random directed disk-valued C;
- three 64-call fixed-offset comparisons (aligned, quarter-turn, anti-phase), with alpha near .5 and the after-call formula `1-alpha^m`;
- one valid large-Tw case whose computed binary alpha is exactly one.

All are clamped/supplied states. The function's phase/delay computation is exercised, but the experiment does **not** advance oscillator phases or claim a production coupled trajectory.

Six deliberately wrong translations were separated from the correct oracle by more than the preregistered `1e-8`:

| Wrong translation | Maximum separation in C or R |
|---|---:|
| Last history instead of oldest | 0.0008206089245647302 |
| Omit mean-omega/tau term | 0.0005476671169744194 |
| Swap alpha and 1-alpha | 1.4586581797385068 |
| Return old R before update | 0.0005161216418710368 |
| Magnitude after complex averaging | 0.09541870614290515 |
| Zero complex diagonal | 0.47518635021693284 |

Comparing C as well as R is important: phase errors can hide in an initial-zero magnitude, and incorrectly zeroing C's diagonal can leave the reported diagonal apparently correct. A zero observed C error in this finite oracle experiment is not a universal bitwise/rounding certificate.

## 6. Explicit protocol correction and float boundary

The original source protocol planned two **valid** floating extremes. Its tiny-Tw case computed binary alpha=0, and the existing `ModelConfig.validate` correctly rejected it (`alpha=0.0 must be in (0, 1]`). The initial run aborted there and its traceback is retained. The original assumption that this was a valid configuration was **ours**, not a repository defect.

The dated protocol correction keeps the same designed case as a **separate expected configuration rejection**, with **no `compute_R` call and no numerical-pass count**. Thus the 35 designed outcomes are accounted for as 34 valid comparisons plus one validation control. No state was substituted, no missing-API/setup failure was called mathematical success, and no allowance was loosened.

The large-Tw case is valid and gives binary alpha=1. This illustrates why exact-real `0<exp(-dt/Tw)<1` cannot be transferred to every accepted binary configuration. The unit-disk theorem deliberately includes alpha=1, while the convergence theorem requires alpha<1. This is a scope boundary, not a claim that baseline runs have alpha=1.

## 7. Reproduce from this single Markdown

All seven critical files are inline below: five Lean sources and two Python checkers. The three reused Lean sources are included only to avoid private imports. The supplied checker is bounded closed-file research tooling, **not a secure Lean intake/parser or a replacement for the seat's trusted compiler/CI**.

### Extract without executing copied code

```bash
PYTHONOPTIMIZE=0 python - /path/to/2026-09-04_researcher040282_004_complex-ema.md /path/to/new-repro <<'PY'
from pathlib import Path
import re, sys
names = {'GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean',
         'CoherenceEMA.lean','CoherenceDriveBridge.lean','check_cycle.py','compare_source.py'}
pattern = r"<!-- FILE: ([A-Za-z_][A-Za-z0-9_]*\.(?:lean|py)) -->\n```[^\n]*\n(.*?)\n```"
matches = re.findall(pattern, Path(sys.argv[1]).read_text(), re.S)
assert len(matches)==7 and set(dict(matches))==names
out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=False)
for name,content in matches:(out/name).write_text(content+'\n')
print('Extracted:', ', '.join(sorted(names)))
PY
```

### Public proof dependencies and execution

Observed compiler: Lean 4.33.1, commit `819816b2e0a3bf405af45ae5c7af2491d8f5bee6`; Mathlib `0df444a360eaa60ab8c11dca51a86af692955474`. These are reproduction metadata, not label/canonical-copy findings. The disposable tool cache was absent and was actually restored and exercised. Selected public Mathlib cache modules were used, not a complete source rebuild of Mathlib.

With that trusted compiler/lake available, in a new owned disposable directory outside frozen AIEFS projects:

```bash
export REPRO=/absolute/path/to/new-repro
export R040282_MATHLIB=/absolute/path/to/new-mathlib4
git clone --depth 1 --branch v4.33.1 \
  https://github.com/leanprover-community/mathlib4.git "$R040282_MATHLIB"
test "$(git -C "$R040282_MATHLIB" rev-parse HEAD)" = \
  0df444a360eaa60ab8c11dca51a86af692955474
cd "$R040282_MATHLIB"
lake exe cache get \
  Mathlib/Algebra/Order/BigOperators/Group/Finset.lean \
  Mathlib/Algebra/BigOperators/Ring/Finset.lean \
  Mathlib/Algebra/Order/Field/Basic.lean \
  Mathlib/Data/Real/Basic.lean \
  Mathlib/Tactic/NormNum.lean \
  Mathlib/Tactic/Linarith.lean \
  Mathlib/Tactic/FieldSimp.lean \
  Mathlib/Tactic/Positivity.lean \
  Mathlib/Tactic/Ring.lean \
  Mathlib/Analysis/SpecificLimits/Basic.lean \
  Mathlib/Analysis/SpecificLimits/Normed.lean \
  Mathlib/Analysis/Complex/Basic.lean \
  Mathlib/Analysis/Complex/Trigonometric.lean
export R040282_LEAN_BIN="$(lake env lean --print-prefix)/bin/lean"
cd "$REPRO"
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python check_cycle.py > cycle_checks.log 2>&1
cat cycle_checks.log
```

The lean executable needs a sibling `lake`; optionally set `R040282_CACHE` to an owned scratch directory. The harness uses only Python's standard library. It verifies the toolchain/pin, freshly compiles all five supplied modules in dependency order with complete axiom coverage, and uses isolated sources/output modules for negative controls. An import failure, timeout, or missing instance is a blocker, not a successful mathematical rejection. Each Lean invocation is bounded at 180 seconds. Run with assertions enabled; no `-O/-OO`.

Expected: checker exit zero, `control_count:18`, all intended outcomes true. Reused module counts `22,5,44`; new positive module counts `22,6`. Eight false mathematical cases must fail mathematically, not on imports. Hole/new-axiom payloads must raw-compile and be policy-rejected; missing coverage must also be rejected.

Exact finite checks alone, without Lean:

```bash
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python check_cycle.py --exact-only
```

### Optional actual-source experiment

Needs NumPy/pandas and the reviewed public engine at the stated source basis. The proof/exact checker does not need them or the engine. The source checker's default local acquisition path will not exist in Markdown-only extraction: set the path explicitly.

```bash
export R040282_AIEFS_ENGINE=/absolute/path/to/reviewed/aief_experiment_engine_v1.py
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python compare_source.py > source_comparison.log 2>&1
```

Expected: 34 valid comparison cases, 253 calls, six detected wrong translations, and one separately expected alpha=0 configuration rejection. This is not 35 valid numerical comparisons. The public source link is in §8. Review code before running it. No repository-owned file is modified.

## 8. Reuse, review request, and remaining work

This follows Cycle 003 (`2026-11-07_researcher040282_003_weight-update-bridge.md`) and preserves its scope, rather than upgrading earlier source tests into proofs. Existing upstream `FreezeCore.lean` is reproduced verbatim with only five audit queries appended and its Apache-2.0 notice retained. **Do not integrate that fixture as duplicate new authoritative definitions.** The 66 earlier local declarations are also reused unchanged.

Requested review actions, not claimed coordination:

- **Researcher 001:** review the state/readout distinction, update-before-readout indexing, actual delayed/mean-omega input, normalization domain, and package/import home. `CoherenceEMA` is independent of the gate library; the drive bridge composes with it. Independently rebuild before any integration. No Lake project, root import, CI workflow, frozen authority, or repository registry was edited here.
- **Auditor Seat 002:** reproduce all wrong-model/trust controls; check that only identical supplied inputs support homogeneous differences; check directed C versus symmetric R, nonzero C/drive diagonals, and the validation correction. Local self-reproduction is not independent-seat approval.
- Keep real proofs, finite exact arithmetic, finite source checks, source semantics, independent review, integration, and publication as separate statuses. No novelty assessment or registry promotion follows from my own compilation.

Still open: the complete delayed phase/history reference transition; a machine-checked Python/float64 linkage; conditions forcing actual long-time drive bands; coupled locking/stability; gated-OFF and finite-network aggregation. A complete weight-map conditional freezing result would still not prove its own coherence-band assumptions.

**Next selected work:** complete the third, gated-OFF matrix-map certificate and finite-edge aggregation, subject to new feedback/source refresh. The newly checked readout/drive component should remain a reusable module, not an excuse to assume constant forcing in the coupled system. The full delayed-state/update specification remains queued next to this work.

### Public references

- [Actual EMA coefficient and validation](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/aief_experiment_engine_v1.py#L150-L228).
- [Initialization and actual compute_R](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/aief_experiment_engine_v1.py#L686-L752).
- [Adaptive proposal and gate](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/aief_experiment_engine_v1.py#L790-L814).
- [Existing upstream scalar core and exclusions](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean).
- [Registry, including retired S11 and scoped freezing rows](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/registry/claims.csv).
- [Current freezing arguments and remaining hypotheses](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/research/freezing/REPORT.md).

The inbox is an intake/navigation source, not the engine tree to merge. The inline proof reproduction requires public Lean/Mathlib, not private workspace access or production trajectory data.
