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

## 9. Observed fresh-build and control evidence

Compiler: `Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)`.

| Module | Credit | Declarations / footprints | Raw Lean exit | Accepted |
|---|---|---:|---:|---|
| GateFoundations | Prior local, unchanged | 22 / 22 | 0 | Yes |
| FreezeCore | Existing upstream, unchanged proof body | 5 / 5 | 0 | Yes |
| GateProposalBridge | Prior local, unchanged | 44 / 44 | 0 | Yes |
| CoherenceEMA | New (helpers included) | 22 / 22 | 0 | Yes |
| CoherenceDriveBridge | New (helpers included) | 6 / 6 | 0 | Yes |

All accepted modules have complete footprint coverage, no warnings/errors, and no axioms outside the allowed standard set. The local full runner exited `0`, with **18 intended outcomes: five positive and thirteen negative**. Its measured elapsed time was 293.11 seconds; runtime is environment-dependent.

| Control | Raw Lean exit | Intended outcome observed |
|---|---:|---|
| `positive_CoherenceEMA` | 0 | Accepted with complete allowed footprints |
| `positive_CoherenceDriveBridge` | 0 | Accepted with complete allowed footprints |
| `false_disk_without_alpha_upper` | 1 | Rejected at a mathematical goal `False`; no dependency error |
| `false_disk_without_alpha_lower` | 1 | Rejected at a mathematical goal `False`; no dependency error |
| `false_disk_without_input_bound` | 1 | Rejected at a mathematical goal `False`; no dependency error |
| `false_unforced_difference` | 1 | Rejected at a mathematical goal `False`; no dependency error |
| `false_complex_average_readout` | 1 | Rejected at a mathematical goal `False`; no dependency error |
| `false_complex_zero_diagonal` | 1 | Rejected at a mathematical goal `False`; no dependency error |
| `false_strict_decay_at_alpha_one` | 1 | Rejected at a mathematical goal `False`; no dependency error |
| `false_coherence_equals_cosine` | 1 | Rejected at a mathematical goal `False`; no dependency error |
| `sorry_payload` | 0 | Raw compilation accepted, verification policy rejected |
| `extra_axiom_payload` | 0 | Raw compilation accepted, verification policy rejected |
| `missing_footprint` | 0 | Raw compilation accepted, verification policy rejected |
| `exact_shared_input_paths` | not a Lean case | Exact finite properties passed |
| `exact_fixed_input_paths` | not a Lean case | Exact finite properties passed |
| `exact_reported_drive_matrices` | not a Lean case | Exact finite properties passed |
| `exact_adversarial_witnesses` | not a Lean case | All eight wrong-variant witnesses refuted exactly |
| `python_optimization_mode` | not a Lean case | Python optimization rejected explicitly (Python exit 2) |

### Actual runner output

```text
Fresh reused dependency and new component/bridge builds, then isolated controls.
GateFoundations PASS declarations 22
FreezeCore PASS declarations 5
GateProposalBridge PASS declarations 44
CoherenceEMA PASS declarations 22
CoherenceDriveBridge PASS declarations 6
positive_CoherenceEMA PASS raw_lean_exit=0
positive_CoherenceDriveBridge PASS raw_lean_exit=0
false_disk_without_alpha_upper PASS raw_lean_exit=1
false_disk_without_alpha_lower PASS raw_lean_exit=1
false_disk_without_input_bound PASS raw_lean_exit=1
false_unforced_difference PASS raw_lean_exit=1
false_complex_average_readout PASS raw_lean_exit=1
false_complex_zero_diagonal PASS raw_lean_exit=1
false_strict_decay_at_alpha_one PASS raw_lean_exit=1
false_coherence_equals_cosine PASS raw_lean_exit=1
sorry_payload PASS raw_lean_exit=0
extra_axiom_payload PASS raw_lean_exit=0
missing_footprint PASS raw_lean_exit=0
exact_shared_input_paths PASS raw_lean_exit=not applicable
exact_fixed_input_paths PASS raw_lean_exit=not applicable
exact_reported_drive_matrices PASS raw_lean_exit=not applicable
exact_adversarial_witnesses PASS raw_lean_exit=not applicable
python_optimization_mode PASS raw_lean_exit=not applicable
All controls passed: True
```

### Accepted axiom footprints (parsed from actual compiler output)

**GateFoundations**

```text
Researcher040282.rowSum_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.nodeScale_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.nodeScale_le_one: [propext, Classical.choice, Quot.sound]
Researcher040282.kernel_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.kernel_le_input: [propext, Classical.choice, Quot.sound]
Researcher040282.kernel_symmetric: [propext, Classical.choice, Quot.sound]
Researcher040282.kernel_zero_diag: [propext, Classical.choice, Quot.sound]
Researcher040282.kernel_row_lower: [propext, Classical.choice, Quot.sound]
Researcher040282.kernel_row_upper: [propext, Classical.choice, Quot.sound]
Researcher040282.kernel_feasible: [propext, Classical.choice, Quot.sound]
Researcher040282.gate_fixes_feasible: [propext, Classical.choice, Quot.sound]
Researcher040282.gate_feasible: [propext, Classical.choice, Quot.sound]
Researcher040282.gate_idempotent: [propext, Classical.choice, Quot.sound]
Researcher040282.gate_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.gate_symmetric: [propext, Classical.choice, Quot.sound]
Researcher040282.gate_zero_diag: [propext, Classical.choice, Quot.sound]
Researcher040282.scale_eq_of_rowSum_eq: [propext, Classical.choice, Quot.sound]
Researcher040282.gate_difference_of_rowSum_eq: [propext, Classical.choice, Quot.sound]
Researcher040282.rat_guard_fixes_boundary: [propext, Classical.choice, Quot.sound]
Researcher040282.rat_kernel_not_idempotent: [propext, Classical.choice, Quot.sound]
Researcher040282.rat_gate_not_nonexpansive: [propext, Classical.choice, Quot.sound]
Researcher040282.rat_negative_epsilon_breaks_capacity: [propext, Classical.choice, Quot.sound]
```

**FreezeCore**

```text
AIEFFreeze.upper_geom: [propext, Classical.choice, Quot.sound]
AIEFFreeze.eventually_off: [propext, Classical.choice, Quot.sound]
AIEFFreeze.eventually_on: [propext, Classical.choice, Quot.sound]
AIEFFreeze.edge_eventually_off: [propext, Classical.choice, Quot.sound]
AIEFFreeze.edge_eventually_on: [propext, Classical.choice, Quot.sound]
```

**GateProposalBridge**

```text
Researcher040282.normalized_affine_identity: [propext, Classical.choice, Quot.sound]
Researcher040282.gap_capacity_iff: [propext, Classical.choice, Quot.sound]
Researcher040282.positiveDrive_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.positiveDriveRow_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.proposal_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.proposal_zero_diag: [propext, Classical.choice, Quot.sound]
Researcher040282.proposal_apply_of_ne: [propext, Classical.choice, Quot.sound]
Researcher040282.proposal_symmetric: [propext, Classical.choice, Quot.sound]
Researcher040282.proposal_eq_symmetrized: [propext, Classical.choice, Quot.sound]
Researcher040282.proposal_entry_upper: [propext, Classical.choice, Quot.sound]
Researcher040282.proposal_row_upper: [propext, Classical.choice, Quot.sound]
Researcher040282.proposal_row_upper_of_feasible: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedFactor_eq_min_appliedNodeScale: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedFactor_comm: [propext, Classical.choice, Quot.sound]
Researcher040282.gate_eq_mul_appliedFactor: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedNodeScale_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedNodeScale_le_one: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedFactor_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedFactor_le_one: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedNodeScale_mul_row_le_capacity: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedFactor_mul_row_le_capacity: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedNodeScale_le_capacity_div_row: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedFactor_le_capacity_div_row: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedFactor_ratio_upper: [propext, Classical.choice, Quot.sound]
Researcher040282.scaleFloor_pos: [propext, Classical.choice, Quot.sound]
Researcher040282.scaleFloor_le_one: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedNodeScale_lower_of_row_upper: [propext, Classical.choice, Quot.sound]
Researcher040282.appliedFactor_lower_of_row_uppers: [propext, Classical.choice, Quot.sound]
Researcher040282.driveEnvelope_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.edgeFloor_pos: [propext, Classical.choice, Quot.sound]
Researcher040282.edgeFloor_le_one: [propext, Classical.choice, Quot.sound]
Researcher040282.weightStep_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.weightStep_feasible: [propext, Classical.choice, Quot.sound]
Researcher040282.weightStep_symmetric: [propext, Classical.choice, Quot.sound]
Researcher040282.weightStep_zero_diag: [propext, Classical.choice, Quot.sound]
Researcher040282.weightStep_scalar_recurrence: [propext, Classical.choice, Quot.sound]
Researcher040282.weightStep_factor_lower_of_drive_bounds: [propext, Classical.choice, Quot.sound]
Researcher040282.trajectory_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.trajectory_feasible_from_first: [propext, Classical.choice, Quot.sound]
Researcher040282.trajectory_good_of_start: [propext, Classical.choice, Quot.sound]
Researcher040282.adaptive_edge_eventually_off: [propext, Classical.choice, Quot.sound]
Researcher040282.adaptive_edge_eventually_on: [propext, Classical.choice, Quot.sound]
Researcher040282.adaptive_edge_eventually_on_from: [propext, Classical.choice, Quot.sound]
Researcher040282.adaptive_edge_eventually_off_from: [propext, Classical.choice, Quot.sound]
```

**CoherenceEMA**

```text
Researcher040282.EMA.phaseInput_norm: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.physicalAlpha_pos: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.physicalAlpha_lt_one: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.emaStep_norm_le: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.emaStep_unitDisk: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.emaTrajectory_unitDisk: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.coherenceUpdate_unitDisk: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.reportedR_nonneg: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.reportedR_symmetric: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.reportedR_diag: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.reportedR_le_one: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.reportedR_lipschitz: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.ema_difference: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.ema_same_input_difference: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.trajectory_same_input_difference: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.trajectory_same_input_norm: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.constant_closed_form: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.constant_error_norm: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.constant_zero_norm: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.constant_converges: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.matrix_same_input_reported_bound: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.constant_zero_reported: [propext, Classical.choice, Quot.sound]
```

**CoherenceDriveBridge**

```text
Researcher040282.EMA.reportedDrive_bounds: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.reportedDrive_symmetric: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.reportedDrive_diag: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.reportedDrive_positiveRow_bound: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.phaseUpdatedDrive_positiveRow_bound: [propext, Classical.choice, Quot.sound]
Researcher040282.EMA.phaseUpdated_gate_floor: [propext, Classical.choice, Quot.sound]
```

### Single-Markdown extraction/reproduction was actually executed

All seven critical files below were extracted from this Markdown into a new directory and matched the supplied sources exactly. The extracted checker freshly rebuilt all five proof modules and repeated all 18 intended control outcomes (exit `0`). The extracted source checker was also executed with the reviewed public engine as an explicit external dependency: 34 comparisons / 253 calls, six wrong-model detections and the separate expected configuration rejection passed again (exit `0`). **This is local self-reproduction, not independent-seat review.**

## Appendix A — Prior guarded finite-map core, unchanged

<!-- FILE: GateFoundations.lean -->
```lean
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Order.Field.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.NormNum

/-!
Finite post-positivity capacity-map foundations.

Scope: exact real arithmetic. The activation guard is part of the definition.
No statement here concerns the complete adaptive phase/EMA/delay evolution or
rounding behavior. Nonnegative node-dependent capacities generalize the uniform
capacity used by the engine. Rational examples below are exact counterexamples.
-/

set_option autoImplicit false

noncomputable section
open scoped BigOperators

namespace Researcher040282

variable {ι : Type*} [Fintype ι]

abbrev Weights (ι : Type*) := ι → ι → ℝ

def rowSum (W : Weights ι) (i : ι) : ℝ := ∑ j, W i j

def nodeScale (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i : ι) : ℝ :=
  min 1 (c i / (rowSum W i + ε))

def kernel (c : ι → ℝ) (ε : ℝ) (W : Weights ι) : Weights ι :=
  fun i j => W i j * min (nodeScale c ε W i) (nodeScale c ε W j)

def feasible (c : ι → ℝ) (W : Weights ι) : Prop :=
  ∀ i, rowSum W i ≤ c i

def gate (c : ι → ℝ) (ε : ℝ) (W : Weights ι) : Weights ι := by
  classical
  exact if feasible c W then W else kernel c ε W

def appliedFactor (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i j : ι) : ℝ := by
  classical
  exact if feasible c W then 1 else min (nodeScale c ε W i) (nodeScale c ε W j)

theorem rowSum_nonneg (W : Weights ι) (hW : ∀ i j, 0 ≤ W i j) (i : ι) :
    0 ≤ rowSum W i := by
  exact Finset.sum_nonneg (fun j _ => hW i j)

theorem nodeScale_nonneg (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) (i : ι) :
    0 ≤ nodeScale c ε W i := by
  apply le_min zero_le_one
  exact div_nonneg (hc i) (le_of_lt (add_pos_of_nonneg_of_pos (rowSum_nonneg W hW i) hε))

theorem nodeScale_le_one (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i : ι) :
    nodeScale c ε W i ≤ 1 :=
  min_le_left _ _

theorem kernel_nonneg (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) :
    ∀ i j, 0 ≤ kernel c ε W i j := by
  intro i j
  exact mul_nonneg (hW i j)
    (le_min (nodeScale_nonneg c ε W hc hε hW i) (nodeScale_nonneg c ε W hc hε hW j))

theorem kernel_le_input (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : ∀ i j, 0 ≤ W i j) (i j : ι) :
    kernel c ε W i j ≤ W i j := by
  calc
    kernel c ε W i j ≤ W i j * 1 :=
      mul_le_mul_of_nonneg_left
        (le_trans (min_le_left _ _) (nodeScale_le_one c ε W i)) (hW i j)
    _ = W i j := mul_one _

theorem kernel_symmetric (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : ∀ i j, W i j = W j i) :
    ∀ i j, kernel c ε W i j = kernel c ε W j i := by
  intro i j
  unfold kernel
  rw [hW i j, min_comm]

theorem kernel_zero_diag (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : ∀ i, W i i = 0) :
    ∀ i, kernel c ε W i i = 0 := by
  intro i
  simp only [kernel, hW i, zero_mul]

theorem kernel_row_lower (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (ℓ : ℝ)
    (hW : ∀ i j, 0 ≤ W i j) (hℓ : ∀ i, ℓ ≤ nodeScale c ε W i) (i : ι) :
    ℓ * rowSum W i ≤ rowSum (kernel c ε W) i := by
  unfold rowSum kernel
  rw [Finset.mul_sum]
  apply Finset.sum_le_sum
  intro j _
  simpa only [mul_comm] using
    mul_le_mul_of_nonneg_left (le_min (hℓ i) (hℓ j)) (hW i j)

theorem kernel_row_upper (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : ∀ i j, 0 ≤ W i j) (i : ι) :
    rowSum (kernel c ε W) i ≤ nodeScale c ε W i * rowSum W i := by
  unfold rowSum kernel
  rw [Finset.mul_sum]
  apply Finset.sum_le_sum
  intro j _
  simpa only [mul_comm] using mul_le_mul_of_nonneg_left
    (min_le_left (nodeScale c ε W i) (nodeScale c ε W j)) (hW i j)

theorem kernel_feasible (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) :
    feasible c (kernel c ε W) := by
  intro i
  have hr : 0 ≤ rowSum W i := rowSum_nonneg W hW i
  have hd : 0 < rowSum W i + ε := add_pos_of_nonneg_of_pos hr hε
  calc
    rowSum (kernel c ε W) i ≤ nodeScale c ε W i * rowSum W i :=
      kernel_row_upper c ε W hW i
    _ ≤ (c i / (rowSum W i + ε)) * rowSum W i :=
      mul_le_mul_of_nonneg_right (min_le_right _ _) hr
    _ ≤ (c i / (rowSum W i + ε)) * (rowSum W i + ε) :=
      mul_le_mul_of_nonneg_left (le_add_of_nonneg_right (le_of_lt hε))
        (div_nonneg (hc i) (le_of_lt hd))
    _ = c i := div_mul_cancel₀ _ (ne_of_gt hd)

theorem gate_fixes_feasible (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : feasible c W) : gate c ε W = W := by
  classical
  simp only [gate, if_pos hW]

theorem gate_feasible (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) :
    feasible c (gate c ε W) := by
  classical
  by_cases hf : feasible c W
  · simpa only [gate, if_pos hf] using hf
  · simpa only [gate, if_neg hf] using kernel_feasible c ε W hc hε hW

theorem gate_idempotent (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) :
    gate c ε (gate c ε W) = gate c ε W :=
  gate_fixes_feasible c ε (gate c ε W) (gate_feasible c ε W hc hε hW)

theorem gate_nonneg (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) :
    ∀ i j, 0 ≤ gate c ε W i j := by
  classical
  by_cases hf : feasible c W
  · simpa only [gate, if_pos hf] using hW
  · simpa only [gate, if_neg hf] using kernel_nonneg c ε W hc hε hW

theorem gate_symmetric (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : ∀ i j, W i j = W j i) :
    ∀ i j, gate c ε W i j = gate c ε W j i := by
  classical
  by_cases hf : feasible c W
  · simpa only [gate, if_pos hf] using hW
  · simpa only [gate, if_neg hf] using kernel_symmetric c ε W hW

theorem gate_zero_diag (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hW : ∀ i, W i i = 0) :
    ∀ i, gate c ε W i i = 0 := by
  classical
  by_cases hf : feasible c W
  · simpa only [gate, if_pos hf] using hW
  · simpa only [gate, if_neg hf] using kernel_zero_diag c ε W hW

theorem scale_eq_of_rowSum_eq (c : ι → ℝ) (ε : ℝ) (U W : Weights ι)
    (h : ∀ i, rowSum U i = rowSum W i) (i : ι) :
    nodeScale c ε U i = nodeScale c ε W i := by
  rw [nodeScale, nodeScale, h i]

theorem gate_difference_of_rowSum_eq (c : ι → ℝ) (ε : ℝ) (U W : Weights ι)
    (h : ∀ i, rowSum U i = rowSum W i) (i j : ι) :
    gate c ε U i j - gate c ε W i j =
      (U i j - W i j) * appliedFactor c ε W i j := by
  classical
  have hiff : feasible c U ↔ feasible c W := by
    simp only [feasible, h]
  by_cases hw : feasible c W
  · have hu : feasible c U := hiff.mpr hw
    simp only [gate, appliedFactor, if_pos hu, if_pos hw, mul_one]
  · have hu : ¬ feasible c U := fun hh => hw (hiff.mp hh)
    simp only [gate, appliedFactor, if_neg hu, if_neg hw, kernel]
    rw [scale_eq_of_rowSum_eq c ε U W h i, scale_eq_of_rowSum_eq c ε U W h j]
    exact (sub_mul _ _ _).symm

-- Exact scalar restrictions of a single-edge example, embeddable in 12 nodes.
def ratKernel (c ε x : ℚ) : ℚ := x * min 1 (c / (x + ε))
def ratGate (c ε x : ℚ) : ℚ := if x ≤ c then x else ratKernel c ε x

theorem rat_guard_fixes_boundary :
    ratGate (19/30) (1/1000000000000) (19/30) = (19/30) := by
  norm_num [ratGate]

theorem rat_kernel_not_idempotent :
    ratKernel (19/30) (1/1000000000000)
      (ratKernel (19/30) (1/1000000000000) (19/30)) ≠
      ratKernel (19/30) (1/1000000000000) (19/30) := by
  norm_num [ratKernel]

theorem rat_gate_not_nonexpansive :
    |ratGate (19/30) (1/1000000000000) ((19/30)+(1/2000000000000)) -
      ratGate (19/30) (1/1000000000000) (19/30)| >
      |((19/30)+(1/2000000000000):ℚ) - (19/30)| := by
  norm_num [ratGate, ratKernel]

theorem rat_negative_epsilon_breaks_capacity :
    ratGate 1 (-1/2) (3/2) > (1:ℚ) := by
  norm_num [ratGate, ratKernel]

end Researcher040282

#print axioms Researcher040282.rowSum_nonneg
#print axioms Researcher040282.nodeScale_nonneg
#print axioms Researcher040282.nodeScale_le_one
#print axioms Researcher040282.kernel_nonneg
#print axioms Researcher040282.kernel_le_input
#print axioms Researcher040282.kernel_symmetric
#print axioms Researcher040282.kernel_zero_diag
#print axioms Researcher040282.kernel_row_lower
#print axioms Researcher040282.kernel_row_upper
#print axioms Researcher040282.kernel_feasible
#print axioms Researcher040282.gate_fixes_feasible
#print axioms Researcher040282.gate_feasible
#print axioms Researcher040282.gate_idempotent
#print axioms Researcher040282.gate_nonneg
#print axioms Researcher040282.gate_symmetric
#print axioms Researcher040282.gate_zero_diag
#print axioms Researcher040282.scale_eq_of_rowSum_eq
#print axioms Researcher040282.gate_difference_of_rowSum_eq
#print axioms Researcher040282.rat_guard_fixes_boundary
#print axioms Researcher040282.rat_kernel_not_idempotent
#print axioms Researcher040282.rat_gate_not_nonexpansive
#print axioms Researcher040282.rat_negative_epsilon_breaks_capacity
```

## Appendix B — Existing upstream scalar core with audit queries

<!-- FILE: FreezeCore.lean -->
```lean
/-
Copyright (c) 2026 Jacob Brainard and AIEF contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: AIEF / SSRH
-/
-- SPDX-License-Identifier: Apache-2.0
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-!
# Finite-time freezing: scalar comparison core (AIEF support-freezing)

Real-arithmetic model of one edge of the AIEF update
  B⁺ = λ · max 0 ((1-h)·B + h·u),   λ ∈ [κ, 1],
with h = γ·dt ∈ (0,1). Status is `B > Bc`.
These lemmas do NOT model the phase dynamics or the R-EMA; the forcing `u`
is an arbitrary sequence and the hypotheses on it are the R-hypotheses.

Scope (see `research/freezing/REPORT.md` §0, §3, §6): these are the scalar comparison core and the
per-edge OFF/ON statements of a *conditional* freezing theorem. The conclusions are existential
(`∃ N`); the explicit `N` of the paper argument is not formalised. Not formalised: the gate row-sum
sandwich (Lemma 1), the gated-OFF certificate (Theorem 3), and anything about phases, delay, the
EMA, or whether the closed loop satisfies the hypotheses (phase-locking with margin is open).
-/

set_option autoImplicit false
set_option linter.style.header false

namespace AIEFFreeze

/-- Affine contraction comparison: x_{n+1} ≤ ρ x_n + β with ρ ∈ [0,1) gives
`x n - U ≤ ρ^n (x 0 - U)` where `U = β/(1-ρ)`. -/
lemma upper_geom (x : ℕ → ℝ) (ρ β : ℝ) (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hstep : ∀ n, x (n + 1) ≤ ρ * x n + β) :
    ∀ n, x n - β / (1 - ρ) ≤ ρ ^ n * (x 0 - β / (1 - ρ)) := by
  have h1 : (1 - ρ) ≠ 0 := by linarith
  intro n
  induction n with
  | zero => simp
  | succ k ih =>
    have key : x (k + 1) - β / (1 - ρ) ≤ ρ * (x k - β / (1 - ρ)) := by
      have : ρ * x k + β - β / (1 - ρ) = ρ * (x k - β / (1 - ρ)) := by
        field_simp; ring
      linarith [hstep k]
    calc x (k + 1) - β / (1 - ρ) ≤ ρ * (x k - β / (1 - ρ)) := key
      _ ≤ ρ * (ρ ^ k * (x 0 - β / (1 - ρ))) := mul_le_mul_of_nonneg_left ih hρ0
      _ = ρ ^ (k + 1) * (x 0 - β / (1 - ρ)) := by ring

/-- OFF freezing: if the comparison fixed point is strictly below the threshold,
the status is eventually (and from then on forever) OFF. -/
theorem eventually_off (x : ℕ → ℝ) (ρ β Bc : ℝ) (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hstep : ∀ n, x (n + 1) ≤ ρ * x n + β) (hgap : β / (1 - ρ) < Bc) :
    ∃ N, ∀ n ≥ N, x n < Bc := by
  set U := β / (1 - ρ)
  set A := |x 0 - U| + 1
  have hA : 0 < A := by positivity
  have hm : 0 < (Bc - U) / A := div_pos (by linarith) hA
  obtain ⟨N, hN⟩ := exists_pow_lt_of_lt_one hm hρ1
  refine ⟨N, fun n hn => ?_⟩
  have hg := upper_geom x ρ β hρ0 hρ1 hstep n
  have hpow : ρ ^ n ≤ ρ ^ N := pow_le_pow_of_le_one hρ0 hρ1.le hn
  have hpn : 0 ≤ ρ ^ n := pow_nonneg hρ0 n
  have h2 : ρ ^ n * (x 0 - U) ≤ ρ ^ n * A :=
    mul_le_mul_of_nonneg_left (by have := le_abs_self (x 0 - U); linarith) hpn
  have h3 : ρ ^ n * A < (Bc - U) / A * A :=
    mul_lt_mul_of_pos_right (lt_of_le_of_lt hpow hN) hA
  rw [div_mul_cancel₀ _ hA.ne'] at h3
  linarith

/-- ON freezing: lower comparison with fixed point strictly above threshold. -/
theorem eventually_on (x : ℕ → ℝ) (ρ β Bc : ℝ) (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hstep : ∀ n, ρ * x n + β ≤ x (n + 1)) (hgap : Bc < β / (1 - ρ)) :
    ∃ N, ∀ n ≥ N, Bc < x n := by
  have h := eventually_off (fun n => - x n) ρ (-β) (-Bc) hρ0 hρ1
    (fun n => by have := hstep n; linarith)
    (by rw [neg_div]; linarith)
  obtain ⟨N, hN⟩ := h
  exact ⟨N, fun n hn => by have := hN n hn; simp at this; linarith⟩

/-- One AIEF edge, OFF case. `lam n ∈ [0,1]` is the (arbitrary, gate-dependent)
scaling factor, `u n ≤ U` the drive. Gate-independent. -/
theorem edge_eventually_off (B u lam : ℕ → ℝ) (h U Bc : ℝ)
    (hh0 : 0 < h) (hh1 : h < 1) (hB0 : 0 ≤ B 0)
    (hlam0 : ∀ n, 0 ≤ lam n) (hlam1 : ∀ n, lam n ≤ 1)
    (hrec : ∀ n, B (n + 1) = lam n * max 0 ((1 - h) * B n + h * u n))
    (hu : ∀ n, u n ≤ U) (hU0 : 0 ≤ U) (hUc : U < Bc) :
    ∃ N, ∀ n ≥ N, B n < Bc := by
  have hnn : ∀ n, 0 ≤ B n := by
    intro n; cases n with
    | zero => exact hB0
    | succ k => rw [hrec k]; exact mul_nonneg (hlam0 k) (le_max_left _ _)
  have hstep : ∀ n, B (n + 1) ≤ (1 - h) * B n + h * U := by
    intro n
    rw [hrec n]
    have hpos : 0 ≤ (1 - h) * B n + h * U :=
      add_nonneg (mul_nonneg (by linarith) (hnn n)) (mul_nonneg hh0.le hU0)
    have hmax : max 0 ((1 - h) * B n + h * u n) ≤ (1 - h) * B n + h * U :=
      max_le hpos (by nlinarith [hu n])
    calc lam n * max 0 ((1 - h) * B n + h * u n)
        ≤ 1 * max 0 ((1 - h) * B n + h * u n) :=
          mul_le_mul_of_nonneg_right (hlam1 n) (le_max_left _ _)
      _ ≤ (1 - h) * B n + h * U := by linarith
  refine eventually_off B (1 - h) (h * U) Bc (by linarith) (by linarith) hstep ?_
  rw [show (1 - (1 - h)) = h by ring, mul_div_cancel_left₀ _ hh0.ne']
  exact hUc

/-- One AIEF edge, ON case, with a uniform lower bound `κ ≤ lam n` on the gate
factor (supplied in the paper argument by Lemma 1 from row-sum bounds) and a
drive lower bound `L ≤ u n`. Fixed point `κ h L / (1 - κ(1-h)) > Bc`. -/
theorem edge_eventually_on (B u lam : ℕ → ℝ) (h κ L Bc : ℝ)
    (hh0 : 0 < h) (hh1 : h < 1) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hlam : ∀ n, κ ≤ lam n)
    (hrec : ∀ n, B (n + 1) = lam n * max 0 ((1 - h) * B n + h * u n))
    (hB0 : 0 ≤ B 0) (hu : ∀ n, L ≤ u n) (hL : 0 ≤ L)
    (hgap : Bc < κ * h * L / (1 - κ * (1 - h))) :
    ∃ N, ∀ n ≥ N, Bc < B n := by
  have hnn : ∀ n, 0 ≤ B n := by
    intro n; cases n with
    | zero => exact hB0
    | succ k => rw [hrec k]; exact mul_nonneg (hκ0.le.trans (hlam k)) (le_max_left _ _)
  have hstep : ∀ n, κ * (1 - h) * B n + κ * h * L ≤ B (n + 1) := by
    intro n
    rw [hrec n]
    have hin : (1 - h) * B n + h * L ≤ max 0 ((1 - h) * B n + h * u n) :=
      le_max_of_le_right (by nlinarith [hu n])
    have hin0 : 0 ≤ (1 - h) * B n + h * L :=
      add_nonneg (mul_nonneg (by linarith) (hnn n)) (mul_nonneg hh0.le hL)
    calc κ * (1 - h) * B n + κ * h * L = κ * ((1 - h) * B n + h * L) := by ring
      _ ≤ lam n * ((1 - h) * B n + h * L) := mul_le_mul_of_nonneg_right (hlam n) hin0
      _ ≤ lam n * max 0 ((1 - h) * B n + h * u n) :=
          mul_le_mul_of_nonneg_left hin (hκ0.le.trans (hlam n))
  exact eventually_on B (κ * (1 - h)) (κ * h * L) Bc
    (mul_nonneg hκ0.le (by linarith)) (by nlinarith) hstep hgap

end AIEFFreeze

-- Local audit queries only; upstream proof body above is unchanged.
#print axioms AIEFFreeze.upper_geom
#print axioms AIEFFreeze.eventually_off
#print axioms AIEFFreeze.eventually_on
#print axioms AIEFFreeze.edge_eventually_off
#print axioms AIEFFreeze.edge_eventually_on
```

## Appendix C — Prior proposal/applied-factor bridge, unchanged

<!-- FILE: GateProposalBridge.lean -->
```lean
import GateFoundations
import FreezeCore
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-!
Exact-real proposal / guarded capacity / scalar-comparison bridge.
The diagonal mask and global guard are explicit. Source-side symmetrization
is identified only under symmetric weights and drive. No theorem here proves
Python/float64 equivalence, phase locking, delayed evolution, or EMA correctness.
-/

set_option autoImplicit false
noncomputable section
open scoped BigOperators

namespace Researcher040282

variable {ι : Type*} [Fintype ι]

def positiveDrive (u : Weights ι) (i j : ι) : ℝ := by
  classical
  exact if i = j then 0 else max 0 (u i j)

def positiveDriveRow (u : Weights ι) (i : ι) : ℝ := ∑ j, positiveDrive u i j

def proposal (h : ℝ) (B u : Weights ι) : Weights ι := by
  classical
  exact fun i j => if i = j then 0 else max 0 ((1-h)*B i j + h*u i j)

def symmetrizedProposal (h : ℝ) (B u : Weights ι) : Weights ι := by
  classical
  exact fun i j => if i = j then 0 else
    (max 0 ((1-h)*B i j+h*u i j) + max 0 ((1-h)*B j i+h*u j i))/2

def appliedNodeScale (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i : ι) : ℝ := by
  classical
  exact if feasible c W then 1 else nodeScale c ε W i

def scaleFloor (c ε M : ℝ) : ℝ := min 1 (c / (M + ε))
def driveEnvelope (c h S : ℝ) : ℝ := (1-h)*c + h*S

def edgeFloor (c ε h Si Sj : ℝ) : ℝ :=
  scaleFloor c ε (max (driveEnvelope c h Si) (driveEnvelope c h Sj))

def weightStep (c ε h : ℝ) (B u : Weights ι) : Weights ι :=
  gate (fun _ => c) ε (proposal h B u)

theorem normalized_affine_identity (γ dt η μ b R : ℝ) (hγ : γ ≠ 0) :
    (1-γ*dt)*b + (γ*dt)*(((η+μ)*R-μ)/γ) =
      b + dt*((η+μ)*R-μ-γ*b) := by
  field_simp [hγ]
  ring

theorem gap_capacity_iff (a δ q r : ℝ) (hq : 0 < q) :
    δ ≤ a-q*r ↔ r ≤ (a-δ)/q := by
  rw [le_div_iff₀ hq]
  constructor <;> intro hh <;> nlinarith

omit [Fintype ι] in
theorem positiveDrive_nonneg (u : Weights ι) (i j : ι) :
    0 ≤ positiveDrive u i j := by
  classical
  unfold positiveDrive
  split_ifs
  · exact le_rfl
  · exact le_max_left _ _

theorem positiveDriveRow_nonneg (u : Weights ι) (i : ι) :
    0 ≤ positiveDriveRow u i := by
  exact Finset.sum_nonneg (fun j _ => positiveDrive_nonneg u i j)

omit [Fintype ι] in
theorem proposal_nonneg (h : ℝ) (B u : Weights ι) :
    ∀ i j, 0 ≤ proposal h B u i j := by
  classical
  intro i j
  unfold proposal
  split_ifs
  · exact le_rfl
  · exact le_max_left _ _

omit [Fintype ι] in
theorem proposal_zero_diag (h : ℝ) (B u : Weights ι) :
    ∀ i, proposal h B u i i = 0 := by
  classical
  intro i
  simp [proposal]

omit [Fintype ι] in
theorem proposal_apply_of_ne (h : ℝ) (B u : Weights ι) (i j : ι) (hij : i ≠ j) :
    proposal h B u i j = max 0 ((1-h)*B i j + h*u i j) := by
  classical
  simp only [proposal, if_neg hij]

omit [Fintype ι] in
theorem proposal_symmetric (h : ℝ) (B u : Weights ι)
    (hB : ∀ i j, B i j = B j i) (hu : ∀ i j, u i j = u j i) :
    ∀ i j, proposal h B u i j = proposal h B u j i := by
  classical
  intro i j
  by_cases hij : i = j
  · subst j; rfl
  · simp only [proposal, if_neg hij, if_neg (Ne.symm hij), hB i j, hu i j]

omit [Fintype ι] in
theorem proposal_eq_symmetrized (h : ℝ) (B u : Weights ι)
    (hB : ∀ i j, B i j = B j i) (hu : ∀ i j, u i j = u j i) (i j : ι) :
    proposal h B u i j = symmetrizedProposal h B u i j := by
  classical
  by_cases hij : i = j
  · simp only [proposal, symmetrizedProposal, if_pos hij]
  · simp only [proposal, symmetrizedProposal, if_neg hij]
    rw [hB j i, hu j i]
    ring

omit [Fintype ι] in
theorem proposal_entry_upper (h : ℝ) (B u : Weights ι)
    (hh0 : 0 ≤ h) (hh1 : h ≤ 1) (hB : ∀ i j, 0 ≤ B i j) (i j : ι) :
    proposal h B u i j ≤ (1-h)*B i j + h*positiveDrive u i j := by
  classical
  have hcoef : 0 ≤ 1-h := sub_nonneg.mpr hh1
  by_cases hij : i = j
  · simp only [proposal, positiveDrive, if_pos hij, mul_zero, add_zero]
    exact mul_nonneg hcoef (hB i j)
  · simp only [proposal, positiveDrive, if_neg hij]
    apply max_le
    · exact add_nonneg (mul_nonneg hcoef (hB i j))
        (mul_nonneg hh0 (le_max_left _ _))
    · exact add_le_add (le_refl _) (mul_le_mul_of_nonneg_left (le_max_right 0 (u i j)) hh0)

theorem proposal_row_upper (h : ℝ) (B u : Weights ι)
    (hh0 : 0 ≤ h) (hh1 : h ≤ 1) (hB : ∀ i j, 0 ≤ B i j) (i : ι) :
    rowSum (proposal h B u) i ≤ (1-h)*rowSum B i + h*positiveDriveRow u i := by
  unfold rowSum
  calc
    (∑ j, proposal h B u i j) ≤ ∑ j, ((1-h)*B i j + h*positiveDrive u i j) :=
      Finset.sum_le_sum (fun j _ => proposal_entry_upper h B u hh0 hh1 hB i j)
    _ = (1-h)*(∑ j, B i j) + h*positiveDriveRow u i := by
      simp only [positiveDriveRow, Finset.sum_add_distrib, Finset.mul_sum]

theorem proposal_row_upper_of_feasible (c h : ℝ) (B u : Weights ι)
    (hh0 : 0 ≤ h) (hh1 : h ≤ 1) (hB : ∀ i j, 0 ≤ B i j)
    (hf : feasible (fun _ => c) B) (i : ι) :
    rowSum (proposal h B u) i ≤ driveEnvelope c h (positiveDriveRow u i) := by
  exact (proposal_row_upper h B u hh0 hh1 hB i).trans
    (add_le_add (mul_le_mul_of_nonneg_left (hf i) (sub_nonneg.mpr hh1)) (le_refl _))

theorem appliedFactor_eq_min_appliedNodeScale (c : ι → ℝ) (ε : ℝ)
    (W : Weights ι) (i j : ι) :
    appliedFactor c ε W i j = min (appliedNodeScale c ε W i) (appliedNodeScale c ε W j) := by
  classical
  by_cases hf : feasible c W <;> simp [appliedFactor, appliedNodeScale, hf]

theorem appliedFactor_comm (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i j : ι) :
    appliedFactor c ε W i j = appliedFactor c ε W j i := by
  rw [appliedFactor_eq_min_appliedNodeScale, appliedFactor_eq_min_appliedNodeScale, min_comm]

theorem gate_eq_mul_appliedFactor (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i j : ι) :
    gate c ε W i j = W i j * appliedFactor c ε W i j := by
  classical
  by_cases hf : feasible c W <;> simp [gate, appliedFactor, kernel, hf]

theorem appliedNodeScale_nonneg (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) (i : ι) :
    0 ≤ appliedNodeScale c ε W i := by
  classical
  by_cases hf : feasible c W
  · simp [appliedNodeScale, hf]
  · simpa only [appliedNodeScale, if_neg hf] using nodeScale_nonneg c ε W hc hε hW i

theorem appliedNodeScale_le_one (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i : ι) :
    appliedNodeScale c ε W i ≤ 1 := by
  classical
  by_cases hf : feasible c W
  · simp [appliedNodeScale, hf]
  · simpa only [appliedNodeScale, if_neg hf] using nodeScale_le_one c ε W i

theorem appliedFactor_nonneg (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) (i j : ι) :
    0 ≤ appliedFactor c ε W i j := by
  rw [appliedFactor_eq_min_appliedNodeScale]
  exact le_min (appliedNodeScale_nonneg c ε W hc hε hW i)
    (appliedNodeScale_nonneg c ε W hc hε hW j)

theorem appliedFactor_le_one (c : ι → ℝ) (ε : ℝ) (W : Weights ι) (i j : ι) :
    appliedFactor c ε W i j ≤ 1 := by
  rw [appliedFactor_eq_min_appliedNodeScale]
  exact (min_le_left _ _).trans (appliedNodeScale_le_one c ε W i)

theorem appliedNodeScale_mul_row_le_capacity (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) (i : ι) :
    appliedNodeScale c ε W i * rowSum W i ≤ c i := by
  classical
  by_cases hf : feasible c W
  · simpa only [appliedNodeScale, if_pos hf, one_mul] using hf i
  · simp only [appliedNodeScale, if_neg hf]
    have hr : 0 ≤ rowSum W i := rowSum_nonneg W hW i
    have hd : 0 < rowSum W i + ε := add_pos_of_nonneg_of_pos hr hε
    calc
      nodeScale c ε W i * rowSum W i ≤ (c i/(rowSum W i+ε))*rowSum W i :=
        mul_le_mul_of_nonneg_right (min_le_right _ _) hr
      _ ≤ (c i/(rowSum W i+ε))*(rowSum W i+ε) :=
        mul_le_mul_of_nonneg_left (le_add_of_nonneg_right hε.le)
          (div_nonneg (hc i) hd.le)
      _ = c i := div_mul_cancel₀ _ hd.ne'

theorem appliedFactor_mul_row_le_capacity (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j) (i j : ι) :
    appliedFactor c ε W i j * rowSum W i ≤ c i := by
  have hfactor : appliedFactor c ε W i j ≤ appliedNodeScale c ε W i := by
    rw [appliedFactor_eq_min_appliedNodeScale]; exact min_le_left _ _
  exact (mul_le_mul_of_nonneg_right hfactor (rowSum_nonneg W hW i)).trans
    (appliedNodeScale_mul_row_le_capacity c ε W hc hε hW i)

theorem appliedNodeScale_le_capacity_div_row (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j)
    (i : ι) (hr : 0 < rowSum W i) :
    appliedNodeScale c ε W i ≤ c i / rowSum W i := by
  exact (le_div_iff₀ hr).mpr (appliedNodeScale_mul_row_le_capacity c ε W hc hε hW i)

theorem appliedFactor_le_capacity_div_row (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j)
    (i j : ι) (hr : 0 < rowSum W i) :
    appliedFactor c ε W i j ≤ c i / rowSum W i := by
  exact (le_div_iff₀ hr).mpr (appliedFactor_mul_row_le_capacity c ε W hc hε hW i j)

theorem appliedFactor_ratio_upper (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j)
    (i j : ι) (hri : 0 < rowSum W i) (hrj : 0 < rowSum W j) :
    appliedFactor c ε W i j ≤ min 1 (min (c i / rowSum W i) (c j / rowSum W j)) := by
  apply le_min (appliedFactor_le_one c ε W i j)
  apply le_min (appliedFactor_le_capacity_div_row c ε W hc hε hW i j hri)
  rw [appliedFactor_comm c ε W i j]
  exact appliedFactor_le_capacity_div_row c ε W hc hε hW j i hrj

theorem scaleFloor_pos (c ε M : ℝ) (hc : 0 < c) (hε : 0 < ε) (hM : 0 ≤ M) :
    0 < scaleFloor c ε M := by
  exact lt_min zero_lt_one (div_pos hc (add_pos_of_nonneg_of_pos hM hε))

theorem scaleFloor_le_one (c ε M : ℝ) : scaleFloor c ε M ≤ 1 := min_le_left _ _

theorem appliedNodeScale_lower_of_row_upper (c : ι → ℝ) (ε : ℝ) (W : Weights ι)
    (hc : ∀ i, 0 ≤ c i) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j)
    (i : ι) (M : ℝ) (hM : rowSum W i ≤ M) :
    scaleFloor (c i) ε M ≤ appliedNodeScale c ε W i := by
  classical
  by_cases hf : feasible c W
  · simpa only [appliedNodeScale, if_pos hf] using scaleFloor_le_one (c i) ε M
  · simp only [appliedNodeScale, if_neg hf]
    have hrpos : 0 < rowSum W i+ε := add_pos_of_nonneg_of_pos (rowSum_nonneg W hW i) hε
    have hMpos : 0 < M+ε := lt_of_lt_of_le hrpos (add_le_add hM (le_refl ε))
    have hdiv : c i/(M+ε) ≤ c i/(rowSum W i+ε) :=
      (div_le_div_iff₀ hMpos hrpos).mpr
        (mul_le_mul_of_nonneg_left (add_le_add hM (le_refl ε)) (hc i))
    exact min_le_min (le_refl 1) hdiv

theorem appliedFactor_lower_of_row_uppers (c ε : ℝ) (W : Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) (hW : ∀ i j, 0 ≤ W i j)
    (i j : ι) (Mi Mj : ℝ) (hi : rowSum W i ≤ Mi) (hj : rowSum W j ≤ Mj) :
    scaleFloor c ε (max Mi Mj) ≤ appliedFactor (fun _ => c) ε W i j := by
  rw [appliedFactor_eq_min_appliedNodeScale]
  exact le_min
    (appliedNodeScale_lower_of_row_upper (fun _ => c) ε W (fun _ => hc) hε hW i _
      (hi.trans (le_max_left _ _)))
    (appliedNodeScale_lower_of_row_upper (fun _ => c) ε W (fun _ => hc) hε hW j _
      (hj.trans (le_max_right _ _)))

theorem driveEnvelope_nonneg (c h S : ℝ) (hc : 0 ≤ c) (hh0 : 0 ≤ h)
    (hh1 : h ≤ 1) (hS : 0 ≤ S) : 0 ≤ driveEnvelope c h S := by
  exact add_nonneg (mul_nonneg (sub_nonneg.mpr hh1) hc) (mul_nonneg hh0 hS)

theorem edgeFloor_pos (c ε h Si Sj : ℝ) (hc : 0 < c) (hε : 0 < ε)
    (hh0 : 0 ≤ h) (hh1 : h ≤ 1) (hSi : 0 ≤ Si) :
    0 < edgeFloor c ε h Si Sj := by
  exact scaleFloor_pos c ε _ hc hε
    ((driveEnvelope_nonneg c h Si hc.le hh0 hh1 hSi).trans (le_max_left _ _))

theorem edgeFloor_le_one (c ε h Si Sj : ℝ) : edgeFloor c ε h Si Sj ≤ 1 :=
  scaleFloor_le_one _ _ _

theorem weightStep_nonneg (c ε h : ℝ) (B u : Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) : ∀ i j, 0 ≤ weightStep c ε h B u i j := by
  exact gate_nonneg (fun _ => c) ε (proposal h B u) (fun _ => hc) hε (proposal_nonneg h B u)

theorem weightStep_feasible (c ε h : ℝ) (B u : Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) : feasible (fun _ => c) (weightStep c ε h B u) := by
  exact gate_feasible (fun _ => c) ε (proposal h B u) (fun _ => hc) hε (proposal_nonneg h B u)

theorem weightStep_symmetric (c ε h : ℝ) (B u : Weights ι)
    (hB : ∀ i j, B i j = B j i) (hu : ∀ i j, u i j = u j i) :
    ∀ i j, weightStep c ε h B u i j = weightStep c ε h B u j i := by
  exact gate_symmetric (fun _ => c) ε (proposal h B u) (proposal_symmetric h B u hB hu)

theorem weightStep_zero_diag (c ε h : ℝ) (B u : Weights ι) :
    ∀ i, weightStep c ε h B u i i = 0 := by
  exact gate_zero_diag (fun _ => c) ε (proposal h B u) (proposal_zero_diag h B u)

theorem weightStep_scalar_recurrence (c ε h : ℝ) (B u : Weights ι)
    (i j : ι) (hij : i ≠ j) :
    weightStep c ε h B u i j = appliedFactor (fun _ => c) ε (proposal h B u) i j *
      max 0 ((1-h)*B i j+h*u i j) := by
  calc
    weightStep c ε h B u i j = proposal h B u i j *
      appliedFactor (fun _ => c) ε (proposal h B u) i j :=
      gate_eq_mul_appliedFactor (fun _ => c) ε (proposal h B u) i j
    _ = _ := by rw [proposal_apply_of_ne h B u i j hij, mul_comm]

theorem weightStep_factor_lower_of_drive_bounds (c ε h : ℝ) (B u : Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) (hh0 : 0 ≤ h) (hh1 : h ≤ 1)
    (hB : ∀ i j, 0 ≤ B i j) (hf : feasible (fun _ => c) B)
    (i j : ι) (Si Sj : ℝ) (hSi : positiveDriveRow u i ≤ Si)
    (hSj : positiveDriveRow u j ≤ Sj) :
    edgeFloor c ε h Si Sj ≤ appliedFactor (fun _ => c) ε (proposal h B u) i j := by
  apply appliedFactor_lower_of_row_uppers c ε (proposal h B u) hc hε
    (proposal_nonneg h B u) i j (driveEnvelope c h Si) (driveEnvelope c h Sj)
  · exact (proposal_row_upper_of_feasible c h B u hh0 hh1 hB hf i).trans
      (add_le_add (le_refl _) (mul_le_mul_of_nonneg_left hSi hh0))
  · exact (proposal_row_upper_of_feasible c h B u hh0 hh1 hB hf j).trans
      (add_le_add (le_refl _) (mul_le_mul_of_nonneg_left hSj hh0))

theorem trajectory_nonneg (c ε h : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) (hB0 : ∀ i j, 0 ≤ B 0 i j)
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n)) :
    ∀ n i j, 0 ≤ B n i j := by
  intro n
  cases n with
  | zero => exact hB0
  | succ n => rw [hrec n]; exact weightStep_nonneg c ε h (B n) (u n) hc hε

theorem trajectory_feasible_from_first (c ε h : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε)
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n)) :
    ∀ n, feasible (fun _ => c) (B (n+1)) := by
  intro n
  rw [hrec n]
  exact weightStep_feasible c ε h (B n) (u n) hc hε

theorem trajectory_good_of_start (c ε h : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) (hB0 : ∀ i j, 0 ≤ B 0 i j)
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n))
    (T : ℕ) (hstart : feasible (fun _ => c) (B 0) ∨ 1 ≤ T) :
    ∀ n, T ≤ n → (∀ i j, 0 ≤ B n i j) ∧ feasible (fun _ => c) (B n) := by
  intro n hn
  cases n with
  | zero =>
      rcases hstart with hf | hT
      · exact ⟨hB0, hf⟩
      · have hbad : (1 : ℕ) ≤ 0 := hT.trans hn
        simp at hbad
  | succ n =>
      rw [hrec n]
      exact ⟨weightStep_nonneg c ε h (B n) (u n) hc hε,
        weightStep_feasible c ε h (B n) (u n) hc hε⟩

theorem adaptive_edge_eventually_off (c ε h U Bc : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) (hh0 : 0 < h) (hh1 : h < 1)
    (i j : ι) (hij : i ≠ j) (hB0 : 0 ≤ B 0 i j)
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n))
    (hu : ∀ n, u n i j ≤ U) (hU0 : 0 ≤ U) (hUc : U < Bc) :
    ∃ N, ∀ n ≥ N, B n i j < Bc := by
  exact AIEFFreeze.edge_eventually_off (fun n => B n i j) (fun n => u n i j)
    (fun n => appliedFactor (fun _ => c) ε (proposal h (B n) (u n)) i j)
    h U Bc hh0 hh1 hB0
    (fun n => appliedFactor_nonneg (fun _ => c) ε _ (fun _ => hc) hε
      (proposal_nonneg h (B n) (u n)) i j)
    (fun n => appliedFactor_le_one (fun _ => c) ε _ i j)
    (fun n => by rw [hrec n]; exact weightStep_scalar_recurrence c ε h (B n) (u n) i j hij)
    hu hU0 hUc

theorem adaptive_edge_eventually_on (c ε h Si Sj L Bc : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 < c) (hε : 0 < ε) (hh0 : 0 < h) (hh1 : h < 1)
    (hB0 : ∀ i j, 0 ≤ B 0 i j) (hf0 : feasible (fun _ => c) (B 0))
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n))
    (i j : ι) (hij : i ≠ j) (hSi : ∀ n, positiveDriveRow (u n) i ≤ Si)
    (hSj : ∀ n, positiveDriveRow (u n) j ≤ Sj)
    (hL : ∀ n, L ≤ u n i j) (hL0 : 0 ≤ L)
    (hgap : Bc < edgeFloor c ε h Si Sj * h * L /
      (1-edgeFloor c ε h Si Sj*(1-h))) :
    ∃ N, ∀ n ≥ N, B n i j > Bc := by
  have hS0 : 0 ≤ Si := (positiveDriveRow_nonneg (u 0) i).trans (hSi 0)
  have hk0 : 0 < edgeFloor c ε h Si Sj := edgeFloor_pos c ε h Si Sj hc hε hh0.le hh1.le hS0
  have hklam : ∀ n, edgeFloor c ε h Si Sj ≤
      appliedFactor (fun _ => c) ε (proposal h (B n) (u n)) i j := by
    intro n
    obtain ⟨hBn, hfn⟩ := trajectory_good_of_start c ε h B u hc.le hε hB0 hrec 0
      (Or.inl hf0) n (Nat.zero_le n)
    exact weightStep_factor_lower_of_drive_bounds c ε h (B n) (u n) hc.le hε
      hh0.le hh1.le hBn hfn i j Si Sj (hSi n) (hSj n)
  exact AIEFFreeze.edge_eventually_on (fun n => B n i j) (fun n => u n i j)
    (fun n => appliedFactor (fun _ => c) ε (proposal h (B n) (u n)) i j)
    h (edgeFloor c ε h Si Sj) L Bc hh0 hh1 hk0 (edgeFloor_le_one _ _ _ _ _) hklam
    (fun n => by rw [hrec n]; exact weightStep_scalar_recurrence c ε h (B n) (u n) i j hij)
    (hB0 i j) hL hL0 hgap

theorem adaptive_edge_eventually_on_from (c ε h Si Sj L Bc : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 < c) (hε : 0 < ε) (hh0 : 0 < h) (hh1 : h < 1)
    (hB0 : ∀ i j, 0 ≤ B 0 i j)
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n))
    (T : ℕ) (hstart : feasible (fun _ => c) (B 0) ∨ 1 ≤ T)
    (i j : ι) (hij : i ≠ j) (hSi : ∀ n, positiveDriveRow (u (T+n)) i ≤ Si)
    (hSj : ∀ n, positiveDriveRow (u (T+n)) j ≤ Sj)
    (hL : ∀ n, L ≤ u (T+n) i j) (hL0 : 0 ≤ L)
    (hgap : Bc < edgeFloor c ε h Si Sj * h * L /
      (1-edgeFloor c ε h Si Sj*(1-h))) :
    ∃ N, ∀ n ≥ N, B (T+n) i j > Bc := by
  obtain ⟨hBT, hfT⟩ := trajectory_good_of_start c ε h B u hc.le hε hB0 hrec T hstart T le_rfl
  apply adaptive_edge_eventually_on c ε h Si Sj L Bc (fun n => B (T+n)) (fun n => u (T+n))
    hc hε hh0 hh1 hBT hfT
    (fun n => by simpa only [Nat.add_assoc] using hrec (T+n))
    i j hij hSi hSj hL hL0 hgap

theorem adaptive_edge_eventually_off_from (c ε h U Bc : ℝ) (B u : ℕ → Weights ι)
    (hc : 0 ≤ c) (hε : 0 < ε) (hh0 : 0 < h) (hh1 : h < 1)
    (hB0 : ∀ i j, 0 ≤ B 0 i j)
    (hrec : ∀ n, B (n+1) = weightStep c ε h (B n) (u n))
    (T : ℕ) (i j : ι) (hij : i ≠ j)
    (hu : ∀ n, u (T+n) i j ≤ U) (hU0 : 0 ≤ U) (hUc : U < Bc) :
    ∃ N, ∀ n ≥ N, B (T+n) i j < Bc := by
  apply adaptive_edge_eventually_off c ε h U Bc (fun n => B (T+n)) (fun n => u (T+n))
    hc hε hh0 hh1 i j hij (trajectory_nonneg c ε h B u hc hε hB0 hrec T i j)
    (fun n => by simpa only [Nat.add_assoc] using hrec (T+n)) hu hU0 hUc

end Researcher040282

#print axioms Researcher040282.normalized_affine_identity
#print axioms Researcher040282.gap_capacity_iff
#print axioms Researcher040282.positiveDrive_nonneg
#print axioms Researcher040282.positiveDriveRow_nonneg
#print axioms Researcher040282.proposal_nonneg
#print axioms Researcher040282.proposal_zero_diag
#print axioms Researcher040282.proposal_apply_of_ne
#print axioms Researcher040282.proposal_symmetric
#print axioms Researcher040282.proposal_eq_symmetrized
#print axioms Researcher040282.proposal_entry_upper
#print axioms Researcher040282.proposal_row_upper
#print axioms Researcher040282.proposal_row_upper_of_feasible
#print axioms Researcher040282.appliedFactor_eq_min_appliedNodeScale
#print axioms Researcher040282.appliedFactor_comm
#print axioms Researcher040282.gate_eq_mul_appliedFactor
#print axioms Researcher040282.appliedNodeScale_nonneg
#print axioms Researcher040282.appliedNodeScale_le_one
#print axioms Researcher040282.appliedFactor_nonneg
#print axioms Researcher040282.appliedFactor_le_one
#print axioms Researcher040282.appliedNodeScale_mul_row_le_capacity
#print axioms Researcher040282.appliedFactor_mul_row_le_capacity
#print axioms Researcher040282.appliedNodeScale_le_capacity_div_row
#print axioms Researcher040282.appliedFactor_le_capacity_div_row
#print axioms Researcher040282.appliedFactor_ratio_upper
#print axioms Researcher040282.scaleFloor_pos
#print axioms Researcher040282.scaleFloor_le_one
#print axioms Researcher040282.appliedNodeScale_lower_of_row_upper
#print axioms Researcher040282.appliedFactor_lower_of_row_uppers
#print axioms Researcher040282.driveEnvelope_nonneg
#print axioms Researcher040282.edgeFloor_pos
#print axioms Researcher040282.edgeFloor_le_one
#print axioms Researcher040282.weightStep_nonneg
#print axioms Researcher040282.weightStep_feasible
#print axioms Researcher040282.weightStep_symmetric
#print axioms Researcher040282.weightStep_zero_diag
#print axioms Researcher040282.weightStep_scalar_recurrence
#print axioms Researcher040282.weightStep_factor_lower_of_drive_bounds
#print axioms Researcher040282.trajectory_nonneg
#print axioms Researcher040282.trajectory_feasible_from_first
#print axioms Researcher040282.trajectory_good_of_start
#print axioms Researcher040282.adaptive_edge_eventually_off
#print axioms Researcher040282.adaptive_edge_eventually_on
#print axioms Researcher040282.adaptive_edge_eventually_on_from
#print axioms Researcher040282.adaptive_edge_eventually_off_from
```

## Appendix D — New complex EMA/readout component

<!-- FILE: CoherenceEMA.lean -->
```lean
/-
Researcher 040282: exact-real complex EMA and reported coherence component.
Prescribed real phase/delayed vectors are inputs, not a proof of coupled locking.
C is directed and may have a nonzero diagonal. Only reported R is symmetrized
and zero-diagonal. The source returns R AFTER updating C.
-/
import Mathlib.Analysis.Complex.Basic
import Mathlib.Analysis.Complex.Trigonometric
import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

set_option autoImplicit false
set_option linter.style.header false

open Filter
open scoped Topology

namespace Researcher040282.EMA

variable {ι : Type*}

abbrev ComplexWeights (ι : Type*) := ι → ι → ℂ

noncomputable def physicalAlpha (dt Tw : ℝ) : ℝ := Real.exp (-dt / Tw)

noncomputable def phaseInput (theta delayed omega : ι → ℝ) (tau : ℝ)
    (i j : ι) : ℂ :=
  Complex.exp (((theta i - delayed j - ((omega i + omega j) / 2) * tau : ℝ) : ℂ) * Complex.I)

noncomputable def emaStep (alpha : ℝ) (C z : ℂ) : ℂ :=
  (alpha : ℂ) * C + ((1 - alpha : ℝ) : ℂ) * z

noncomputable def emaTrajectory (alpha : ℝ) (C0 : ℂ) (z : ℕ → ℂ) : ℕ → ℂ
  | 0 => C0
  | n + 1 => emaStep alpha (emaTrajectory alpha C0 z n) (z n)

noncomputable def coherenceUpdate (alpha : ℝ) (C : ComplexWeights ι)
    (theta delayed omega : ι → ℝ) (tau : ℝ) : ComplexWeights ι :=
  fun i j => emaStep alpha (C i j) (phaseInput theta delayed omega tau i j)

noncomputable def reportedR (C : ComplexWeights ι) (i j : ι) : ℝ := by
  classical
  exact if i = j then 0 else (‖C i j‖ + ‖C j i‖) / 2

noncomputable def matrixTrajectory (alpha : ℝ) (C0 : ComplexWeights ι)
    (z : ℕ → ComplexWeights ι) (n : ℕ) : ComplexWeights ι :=
  fun i j => emaTrajectory alpha (C0 i j) (fun m => z m i j) n

theorem phaseInput_norm (theta delayed omega : ι → ℝ) (tau : ℝ) (i j : ι) :
    ‖phaseInput theta delayed omega tau i j‖ = 1 := by
  simp [phaseInput, Complex.norm_exp]

theorem physicalAlpha_pos (dt Tw : ℝ) : 0 < physicalAlpha dt Tw :=
  Real.exp_pos _

theorem physicalAlpha_lt_one (dt Tw : ℝ) (hdt : 0 < dt) (hTw : 0 < Tw) :
    physicalAlpha dt Tw < 1 := by
  rw [physicalAlpha, Real.exp_lt_one_iff, neg_div]
  have := div_pos hdt hTw
  linarith

theorem emaStep_norm_le (alpha : ℝ) (C z : ℂ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) :
    ‖emaStep alpha C z‖ ≤ alpha * ‖C‖ + (1-alpha) * ‖z‖ := by
  calc
    ‖emaStep alpha C z‖ ≤ ‖(alpha : ℂ) * C‖ + ‖((1-alpha : ℝ) : ℂ) * z‖ :=
      norm_add_le _ _
    _ = alpha * ‖C‖ + (1-alpha) * ‖z‖ := by
      rw [norm_mul, norm_mul, Complex.norm_of_nonneg ha0,
        Complex.norm_of_nonneg (sub_nonneg.mpr ha1)]

theorem emaStep_unitDisk (alpha : ℝ) (C z : ℂ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ‖C‖ ≤ 1) (hz : ‖z‖ ≤ 1) :
    ‖emaStep alpha C z‖ ≤ 1 := by
  calc
    ‖emaStep alpha C z‖ ≤ alpha * ‖C‖ + (1-alpha) * ‖z‖ :=
      emaStep_norm_le alpha C z ha0 ha1
    _ ≤ alpha * 1 + (1-alpha) * 1 :=
      add_le_add (mul_le_mul_of_nonneg_left hC ha0)
        (mul_le_mul_of_nonneg_left hz (sub_nonneg.mpr ha1))
    _ = 1 := by ring

theorem emaTrajectory_unitDisk (alpha : ℝ) (C0 : ℂ) (z : ℕ → ℂ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ‖C0‖ ≤ 1)
    (hz : ∀ n, ‖z n‖ ≤ 1) : ∀ n, ‖emaTrajectory alpha C0 z n‖ ≤ 1 := by
  intro n
  induction n with
  | zero => exact hC
  | succ n ih => exact emaStep_unitDisk alpha _ _ ha0 ha1 ih (hz n)

theorem coherenceUpdate_unitDisk (alpha : ℝ) (C : ComplexWeights ι)
    (theta delayed omega : ι → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C i j‖ ≤ 1) :
    ∀ i j, ‖coherenceUpdate alpha C theta delayed omega tau i j‖ ≤ 1 := by
  intro i j
  exact emaStep_unitDisk alpha _ _ ha0 ha1 (hC i j)
    (phaseInput_norm theta delayed omega tau i j).le

theorem reportedR_nonneg (C : ComplexWeights ι) (i j : ι) :
    0 ≤ reportedR C i j := by
  classical
  unfold reportedR
  split_ifs <;> positivity

theorem reportedR_symmetric (C : ComplexWeights ι) (i j : ι) :
    reportedR C i j = reportedR C j i := by
  classical
  by_cases h : i = j
  · subst j; rfl
  · simp only [reportedR, if_neg h, if_neg (Ne.symm h)]
    ring

theorem reportedR_diag (C : ComplexWeights ι) (i : ι) : reportedR C i i = 0 := by
  simp [reportedR]

theorem reportedR_le_one (C : ComplexWeights ι) (hC : ∀ i j, ‖C i j‖ ≤ 1) (i j : ι) :
    reportedR C i j ≤ 1 := by
  classical
  by_cases h : i = j
  · simp [reportedR, h]
  · simp only [reportedR, if_neg h]
    have := hC i j
    have := hC j i
    linarith

theorem reportedR_lipschitz (C D : ComplexWeights ι) (i j : ι) :
    |reportedR C i j - reportedR D i j| ≤
      (‖C i j - D i j‖ + ‖C j i - D j i‖) / 2 := by
  classical
  by_cases h : i = j
  · subst j
    rw [reportedR_diag, reportedR_diag, sub_self, abs_zero]
    exact div_nonneg (add_nonneg (norm_nonneg _) (norm_nonneg _)) (by norm_num)
  · simp only [reportedR, if_neg h]
    have h1 := abs_norm_sub_norm_le (C i j) (D i j)
    have h2 := abs_norm_sub_norm_le (C j i) (D j i)
    rw [show (‖C i j‖ + ‖C j i‖) / 2 - (‖D i j‖ + ‖D j i‖) / 2 =
      ((‖C i j‖ - ‖D i j‖) + (‖C j i‖ - ‖D j i‖)) / 2 by ring,
      abs_div, abs_of_pos (by norm_num : (0 : ℝ) < 2)]
    exact div_le_div_of_nonneg_right
      ((abs_add_le _ _).trans (add_le_add h1 h2)) (by norm_num)

theorem ema_difference (alpha : ℝ) (C D z w : ℂ) :
    emaStep alpha C z - emaStep alpha D w =
      (alpha : ℂ) * (C-D) + ((1-alpha : ℝ) : ℂ) * (z-w) := by
  unfold emaStep
  ring

theorem ema_same_input_difference (alpha : ℝ) (C D z : ℂ) :
    emaStep alpha C z - emaStep alpha D z = (alpha : ℂ) * (C-D) := by
  rw [ema_difference, sub_self, mul_zero, add_zero]

theorem trajectory_same_input_difference (alpha : ℝ) (C0 D0 : ℂ)
    (z : ℕ → ℂ) (n : ℕ) :
    emaTrajectory alpha C0 z n - emaTrajectory alpha D0 z n =
      (alpha : ℂ)^n * (C0-D0) := by
  induction n with
  | zero => simp [emaTrajectory]
  | succ n ih =>
    change emaStep alpha (emaTrajectory alpha C0 z n) (z n) -
      emaStep alpha (emaTrajectory alpha D0 z n) (z n) = _
    rw [ema_same_input_difference, ih, pow_succ]
    ring

theorem trajectory_same_input_norm (alpha : ℝ) (C0 D0 : ℂ)
    (z : ℕ → ℂ) (n : ℕ) (ha0 : 0 ≤ alpha) :
    ‖emaTrajectory alpha C0 z n - emaTrajectory alpha D0 z n‖ =
      alpha^n * ‖C0-D0‖ := by
  rw [trajectory_same_input_difference, norm_mul, norm_pow, Complex.norm_of_nonneg ha0]

theorem constant_closed_form (alpha : ℝ) (C0 z : ℂ) (n : ℕ) :
    emaTrajectory alpha C0 (fun _ => z) n = z + (alpha : ℂ)^n * (C0-z) := by
  induction n with
  | zero =>
    simp only [emaTrajectory, pow_zero, one_mul]
    ring
  | succ n ih =>
    change emaStep alpha (emaTrajectory alpha C0 (fun _ => z) n) z = _
    rw [ih]
    simp only [emaStep, pow_succ]
    push_cast
    ring

theorem constant_error_norm (alpha : ℝ) (C0 z : ℂ) (n : ℕ) (ha0 : 0 ≤ alpha) :
    ‖emaTrajectory alpha C0 (fun _ => z) n - z‖ = alpha^n * ‖C0-z‖ := by
  rw [constant_closed_form]
  rw [show z + (alpha : ℂ)^n * (C0-z) - z = (alpha : ℂ)^n * (C0-z) by ring]
  rw [norm_mul, norm_pow, Complex.norm_of_nonneg ha0]

theorem constant_zero_norm (alpha : ℝ) (z : ℂ) (n : ℕ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hz : ‖z‖ = 1) :
    ‖emaTrajectory alpha 0 (fun _ => z) n‖ = 1-alpha^n := by
  have heq : emaTrajectory alpha 0 (fun _ => z) n = ((1-alpha^n : ℝ) : ℂ) * z := by
    rw [constant_closed_form]
    push_cast
    ring
  rw [heq, norm_mul, Complex.norm_of_nonneg (sub_nonneg.mpr (pow_le_one₀ ha0 ha1)),
    hz, mul_one]

theorem constant_converges (alpha : ℝ) (C0 z : ℂ) (ha0 : 0 ≤ alpha) (ha1 : alpha < 1) :
    Tendsto (emaTrajectory alpha C0 (fun _ => z)) atTop (𝓝 z) := by
  have hp : Tendsto (fun n : ℕ => (alpha : ℂ)^n) atTop (𝓝 0) :=
    tendsto_pow_atTop_nhds_zero_of_norm_lt_one (by
      rw [Complex.norm_of_nonneg ha0]
      exact ha1)
  have ht : Tendsto (fun n : ℕ => z + (alpha : ℂ)^n * (C0-z)) atTop
      (𝓝 (z + 0 * (C0-z))) := tendsto_const_nhds.add (hp.mul_const (C0-z))
  have heq : emaTrajectory alpha C0 (fun _ => z) =
      (fun n => z + (alpha : ℂ)^n * (C0-z)) :=
    funext (fun n => constant_closed_form alpha C0 z n)
  rw [heq]
  simpa only [zero_mul, add_zero] using ht

theorem matrix_same_input_reported_bound (alpha : ℝ) (C0 D0 : ComplexWeights ι)
    (z : ℕ → ComplexWeights ι) (n : ℕ) (ha0 : 0 ≤ alpha) (i j : ι) :
    |reportedR (matrixTrajectory alpha C0 z n) i j -
      reportedR (matrixTrajectory alpha D0 z n) i j| ≤
      alpha^n * (‖C0 i j - D0 i j‖ + ‖C0 j i - D0 j i‖) / 2 := by
  calc
    _ ≤ (‖matrixTrajectory alpha C0 z n i j - matrixTrajectory alpha D0 z n i j‖ +
        ‖matrixTrajectory alpha C0 z n j i - matrixTrajectory alpha D0 z n j i‖) / 2 :=
      reportedR_lipschitz _ _ i j
    _ = _ := by
      simp only [matrixTrajectory, trajectory_same_input_norm alpha _ _ _ n ha0]
      ring

theorem constant_zero_reported (alpha : ℝ) (z : ComplexWeights ι) (n : ℕ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hz : ∀ i j, ‖z i j‖ = 1)
    (i j : ι) (hij : i ≠ j) :
    reportedR (matrixTrajectory alpha (fun _ _ => 0) (fun _ => z) n) i j =
      1-alpha^n := by
  simp only [reportedR, if_neg hij, matrixTrajectory]
  rw [constant_zero_norm alpha (z i j) n ha0 ha1 (hz i j),
    constant_zero_norm alpha (z j i) n ha0 ha1 (hz j i)]
  ring

end Researcher040282.EMA

-- Closed-file audit queries.
#print axioms Researcher040282.EMA.phaseInput_norm
#print axioms Researcher040282.EMA.physicalAlpha_pos
#print axioms Researcher040282.EMA.physicalAlpha_lt_one
#print axioms Researcher040282.EMA.emaStep_norm_le
#print axioms Researcher040282.EMA.emaStep_unitDisk
#print axioms Researcher040282.EMA.emaTrajectory_unitDisk
#print axioms Researcher040282.EMA.coherenceUpdate_unitDisk
#print axioms Researcher040282.EMA.reportedR_nonneg
#print axioms Researcher040282.EMA.reportedR_symmetric
#print axioms Researcher040282.EMA.reportedR_diag
#print axioms Researcher040282.EMA.reportedR_le_one
#print axioms Researcher040282.EMA.reportedR_lipschitz
#print axioms Researcher040282.EMA.ema_difference
#print axioms Researcher040282.EMA.ema_same_input_difference
#print axioms Researcher040282.EMA.trajectory_same_input_difference
#print axioms Researcher040282.EMA.trajectory_same_input_norm
#print axioms Researcher040282.EMA.constant_closed_form
#print axioms Researcher040282.EMA.constant_error_norm
#print axioms Researcher040282.EMA.constant_zero_norm
#print axioms Researcher040282.EMA.constant_converges
#print axioms Researcher040282.EMA.matrix_same_input_reported_bound
#print axioms Researcher040282.EMA.constant_zero_reported
```

## Appendix E — New reported-drive/gate bridge

<!-- FILE: CoherenceDriveBridge.lean -->
```lean
/-
Researcher 040282: connect the actual reported-coherence expression to the prior
positive-drive row and gate-floor model. Exact-real component composition only.
A uniform range envelope does not prove sharp ON bands or coupled locking.
-/
import CoherenceEMA
import GateProposalBridge

set_option autoImplicit false
set_option linter.style.header false

namespace Researcher040282.EMA

variable {ι : Type*}

noncomputable def normalizedDrive (eta mu gamma : ℝ) (R : ι → ι → ℝ) (i j : ι) : ℝ :=
  ((eta+mu)*R i j-mu)/gamma

noncomputable def degreeDriveBound (ι : Type*) [Fintype ι] (eta gamma : ℝ) : ℝ :=
  ((Fintype.card ι - 1 : ℕ) : ℝ) * (eta/gamma)

theorem reportedDrive_bounds (eta mu gamma : ℝ) (C : ComplexWeights ι)
    (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (hgamma : 0 < gamma)
    (hC : ∀ i j, ‖C i j‖ ≤ 1) (i j : ι) :
    -mu/gamma ≤ normalizedDrive eta mu gamma (reportedR C) i j ∧
      normalizedDrive eta mu gamma (reportedR C) i j ≤ eta/gamma := by
  have hR0 := reportedR_nonneg C i j
  have hR1 := reportedR_le_one C hC i j
  dsimp only [normalizedDrive]
  constructor
  · apply (div_le_div_iff_of_pos_right hgamma).2
    nlinarith [mul_nonneg (add_nonneg heta hmu) hR0]
  · apply (div_le_div_iff_of_pos_right hgamma).2
    nlinarith [mul_le_mul_of_nonneg_left hR1 (add_nonneg heta hmu)]

theorem reportedDrive_symmetric (eta mu gamma : ℝ) (C : ComplexWeights ι) (i j : ι) :
    normalizedDrive eta mu gamma (reportedR C) i j =
      normalizedDrive eta mu gamma (reportedR C) j i := by
  unfold normalizedDrive
  rw [reportedR_symmetric C i j]

theorem reportedDrive_diag (eta mu gamma : ℝ) (C : ComplexWeights ι) (i : ι) :
    normalizedDrive eta mu gamma (reportedR C) i i = -mu/gamma := by
  simp [normalizedDrive, reportedR]

section Finite

variable [Fintype ι]

theorem reportedDrive_positiveRow_bound (eta mu gamma : ℝ) (C : ComplexWeights ι)
    (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (hgamma : 0 < gamma)
    (hC : ∀ i j, ‖C i j‖ ≤ 1) (i : ι) :
    positiveDriveRow (normalizedDrive eta mu gamma (reportedR C)) i ≤
      degreeDriveBound ι eta gamma := by
  classical
  let u := normalizedDrive eta mu gamma (reportedR C)
  have he : (∑ j ∈ (Finset.univ : Finset ι).erase i, positiveDrive u i j) =
      positiveDriveRow u i := Finset.sum_erase _ (by simp [positiveDrive])
  change positiveDriveRow u i ≤ _
  rw [← he]
  calc
    (∑ j ∈ (Finset.univ : Finset ι).erase i, positiveDrive u i j) ≤
        ∑ j ∈ (Finset.univ : Finset ι).erase i, eta/gamma := by
      apply Finset.sum_le_sum
      intro j hj
      have hji : j ≠ i := (Finset.mem_erase.mp hj).1
      simp only [positiveDrive, if_neg (Ne.symm hji)]
      exact max_le (div_nonneg heta hgamma.le)
        (reportedDrive_bounds eta mu gamma C heta hmu hgamma hC i j).2
    _ = degreeDriveBound ι eta gamma := by
      simp only [Finset.sum_const, Finset.card_erase_of_mem (Finset.mem_univ i),
        Finset.card_univ, nsmul_eq_mul, degreeDriveBound]

theorem phaseUpdatedDrive_positiveRow_bound (alpha eta mu gamma : ℝ)
    (C : ComplexWeights ι) (theta delayed omega : ι → ℝ) (tau : ℝ)
    (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1) (hC : ∀ i j, ‖C i j‖ ≤ 1)
    (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (hgamma : 0 < gamma) (i : ι) :
    positiveDriveRow (normalizedDrive eta mu gamma
      (reportedR (coherenceUpdate alpha C theta delayed omega tau))) i ≤
        degreeDriveBound ι eta gamma :=
  reportedDrive_positiveRow_bound eta mu gamma _ heta hmu hgamma
    (coherenceUpdate_unitDisk alpha C theta delayed omega tau ha0 ha1 hC) i

theorem phaseUpdated_gate_floor (alpha eta mu gamma c eps h : ℝ)
    (C : ComplexWeights ι) (theta delayed omega : ι → ℝ) (tau : ℝ)
    (B : Weights ι) (ha0 : 0 ≤ alpha) (ha1 : alpha ≤ 1)
    (hC : ∀ i j, ‖C i j‖ ≤ 1)
    (heta : 0 ≤ eta) (hmu : 0 ≤ mu) (hgamma : 0 < gamma)
    (hc : 0 ≤ c) (heps : 0 < eps) (hh0 : 0 ≤ h) (hh1 : h ≤ 1)
    (hB : ∀ i j, 0 ≤ B i j) (hfeas : feasible (fun _ => c) B) (i j : ι) :
    edgeFloor c eps h (degreeDriveBound ι eta gamma) (degreeDriveBound ι eta gamma) ≤
      appliedFactor (fun _ => c) eps (proposal h B (normalizedDrive eta mu gamma
        (reportedR (coherenceUpdate alpha C theta delayed omega tau)))) i j := by
  apply weightStep_factor_lower_of_drive_bounds c eps h B _ hc heps hh0 hh1 hB hfeas
    i j (degreeDriveBound ι eta gamma) (degreeDriveBound ι eta gamma)
  · exact phaseUpdatedDrive_positiveRow_bound alpha eta mu gamma C theta delayed omega tau
      ha0 ha1 hC heta hmu hgamma i
  · exact phaseUpdatedDrive_positiveRow_bound alpha eta mu gamma C theta delayed omega tau
      ha0 ha1 hC heta hmu hgamma j

end Finite
end Researcher040282.EMA

-- Closed-file audit queries.
#print axioms Researcher040282.EMA.reportedDrive_bounds
#print axioms Researcher040282.EMA.reportedDrive_symmetric
#print axioms Researcher040282.EMA.reportedDrive_diag
#print axioms Researcher040282.EMA.reportedDrive_positiveRow_bound
#print axioms Researcher040282.EMA.phaseUpdatedDrive_positiveRow_bound
#print axioms Researcher040282.EMA.phaseUpdated_gate_floor
```

## Appendix F — Complete bounded proof/exact checker

<!-- FILE: check_cycle.py -->
```python
"""Fresh complex-EMA/drive builds and bounded adversarial controls.

This closed-file research harness is not a secure general Lean parser/executor
or a replacement for the receiving seat's trusted compiler and repository CI.
"""
from __future__ import annotations
import sys
if not __debug__:
    print('Python assertions must be enabled; do not use -O/-OO.', file=sys.stderr)
    raise SystemExit(2)
import argparse
import concurrent.futures
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parent
CACHE=Path(os.environ.get('R040282_CACHE',Path.home()/'.cache/researcher040282')).expanduser().resolve()
MATHLIB=Path(os.environ.get('R040282_MATHLIB',CACHE/'mathlib4')).expanduser().resolve()
LEAN=Path(os.environ.get('R040282_LEAN_BIN',CACHE/'lean-4.33.1-linux/bin/lean')).expanduser().absolute()
LAKE=LEAN.parent/'lake'
REVISION='0df444a360eaa60ab8c11dca51a86af692955474'
ALLOWED={'propext','Classical.choice','Quot.sound'}
FILES=['GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean','CoherenceEMA.lean','CoherenceDriveBridge.lean']
LOGS=ROOT/'checks'


def without_comments_and_strings(text):
    result=[];i=0;depth=0;string=False
    while i<len(text):
        if depth:
            if text.startswith('/-',i):depth+=1;result.extend('  ');i+=2
            elif text.startswith('-/',i):depth-=1;result.extend('  ');i+=2
            else:result.append('\n' if text[i]=='\n' else ' ');i+=1
        elif string:
            if text[i]=='\\' and i+1<len(text):result.extend('  ');i+=2
            elif text[i]=='"':string=False;result.append(' ');i+=1
            else:result.append('\n' if text[i]=='\n' else ' ');i+=1
        elif text.startswith('/-',i):depth=1;result.extend('  ');i+=2
        elif text.startswith('--',i):
            end=text.find('\n',i)
            if end<0:end=len(text)
            result.extend(' '*(end-i));i=end
        elif text[i]=='"':string=True;result.append(' ');i+=1
        else:result.append(text[i]);i+=1
    if depth or string:raise ValueError('Unterminated source comment or string')
    return ''.join(result)


def assess(source,returncode,output):
    code=without_comments_and_strings(source);problems=[]
    if returncode!=0:problems.append('compiler_nonzero')
    if re.search(r'\bwarning\b',output,re.I):problems.append('compiler_warning')
    forbidden=sorted(set(re.findall(r'\b(?:sorry|admit|native_decide|axiom|unsafe)\b',code)))
    if forbidden:problems.append('forbidden_source_token:'+','.join(forbidden))
    declarations=re.findall(r'(?m)^(?:theorem|lemma)\s+([A-Za-z0-9_]+)',code)
    requested=re.findall(r'(?m)^#print\s+axioms\s+([A-Za-z0-9_.]+)',code)
    if sorted(declarations)!=sorted(n.rsplit('.',1)[-1] for n in requested):
        problems.append('theorem_axiom_print_coverage')
    footprints={name:[v.strip() for v in values.split(',') if v.strip()]
        for name,values in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",output)}
    for name in re.findall(r"'([^']+)' does not depend on any axioms",output):footprints[name]=[]
    for name in requested:
        if name not in footprints:problems.append('missing_axiom_output:'+name)
    for name,values in footprints.items():
        if set(values)-ALLOWED:problems.append('unapproved_axioms:'+name+':'+','.join(sorted(set(values)-ALLOWED)))
    return {'verified':not problems,'problems':problems,'declaration_count':len(declarations),
            'axiom_footprints':footprints}


def compile_one(name,source,directory,env,log_name=None):
    path=directory/(name+'.lean');path.write_text(source);started=time.perf_counter()
    run=subprocess.run([str(LEAN),'--root='+str(directory),'-o',str(directory/(name+'.olean')),str(path)],
        cwd=MATHLIB,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    elapsed=time.perf_counter()-started
    (LOGS/((log_name or name)+'.log')).write_text(run.stdout)
    return run,elapsed


def compile_case(item,dependencies,env):
    name,source,kind=item
    with tempfile.TemporaryDirectory(prefix='r040282-c004-'+name+'-',dir=CACHE) as tmp:
        directory=Path(tmp);local_env=env.copy()
        local_env['LEAN_PATH']=str(directory)+os.pathsep+str(dependencies)+os.pathsep+env.get('LEAN_PATH','')
        run,elapsed=compile_one('Candidate',source,directory,local_env,log_name=name)
    # Each case has its own source, output module and durable log.
    checked=assess(source,run.returncode,run.stdout)
    math_error=bool(re.search(r'unsolved goals|type mismatch|tactic.*failed',run.stdout,re.I))
    dependency_error=bool(re.search(r'unknown module|unknown constant|unknown identifier|object file.*does not exist|failed to import|synthInstanceFailed',run.stdout,re.I))
    if kind=='positive':ok=run.returncode==0 and checked['verified']
    elif kind=='false_math':ok=run.returncode!=0 and math_error and not dependency_error and not checked['verified']
    elif kind=='sorry_payload':ok=run.returncode==0 and not checked['verified'] and any('sorryAx' in p for p in checked['problems'])
    elif kind=='extra_axiom_payload':ok=run.returncode==0 and not checked['verified'] and any('unapproved_axioms:' in p for p in checked['problems'])
    elif kind=='missing_footprint':ok=run.returncode==0 and not checked['verified'] and 'theorem_axiom_print_coverage' in checked['problems']
    else:raise ValueError(kind)
    return {'case':name,'kind':kind,'control_passed':ok,'raw_lean_exit':run.returncode,
            'seconds':elapsed,'mathematical_error_observed':math_error,
            'dependency_error_observed':dependency_error,**checked}


# Independent exact Gaussian-rational arithmetic, not NumPy/cmath or Lean evaluation.
def gadd(z,w):return (z[0]+w[0],z[1]+w[1])
def gsub(z,w):return (z[0]-w[0],z[1]-w[1])
def gscale(a,z):return (a*z[0],a*z[1])
def normsq(z):return z[0]*z[0]+z[1]*z[1]
def step(a,c,z):return gadd(gscale(a,c),gscale(1-a,z))
ZERO=(F(0),F(0));ONE=(F(1),F(0));NEGONE=(F(-1),F(0))
POINTS=[ONE,NEGONE,(F(0),F(1)),(F(0),F(-1)),(F(3,5),F(4,5)),(F(-3,5),F(4,5)),(F(5,13),F(-12,13))]
ALPHAS=[F(0),F(1),F(1,4),F(1,2),F(9,10),F(1,10**6),1-F(1,10**6)]


def exact_controls():
    rng=random.Random(20260904);disk_checks=0;difference_checks=0;fixed_checks=0
    for k in range(64):
        a=ALPHAS[k%len(ALPHAS)]
        c0=gscale(F(rng.randrange(21),20),rng.choice(POINTS));d0=gscale(F(rng.randrange(21),20),rng.choice(POINTS))
        c,d=c0,d0
        for n in range(17):
            assert normsq(c)<=1 and normsq(d)<=1;disk_checks+=2
            assert gsub(c,d)==gscale(a**n,gsub(c0,d0));difference_checks+=1
            assert normsq(gsub(c,d))==a**(2*n)*normsq(gsub(c0,d0))
            if n<16:
                z=rng.choice(POINTS);assert normsq(z)==1
                c,d=step(a,c,z),step(a,d,z)
    for k in range(64):
        a=ALPHAS[k%len(ALPHAS)];z=rng.choice(POINTS)
        c0=gscale(F(rng.randrange(21),20),rng.choice(POINTS));c=c0;zero_path=ZERO
        for n in range(17):
            assert c==gadd(z,gscale(a**n,gsub(c0,z)))
            assert normsq(gsub(c,z))==a**(2*n)*normsq(gsub(c0,z))
            assert normsq(c)<=1 and normsq(zero_path)==(1-a**n)**2;fixed_checks+=1
            if n<16:c,zero_path=step(a,c,z),step(a,zero_path,z)
    matrix_count=0;tight_rows=0;nodes=[1,2,3,6,12]
    for k in range(120):
        n=nodes[k%len(nodes)];eta=rng.choice([F(0),F(1,25),F(1)])
        mu=rng.choice([F(0),F(3,100),F(2)]);gamma=rng.choice([F(3,200),F(1,10),F(1)])
        R=[[F(0) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(i):R[i][j]=R[j][i]=F(1) if k%3==0 else F(rng.randrange(21),20)
        # These R are realized by real nonnegative off-diagonal C, with arbitrary
        # disk-valued complex diagonal subsequently masked only by the readout.
        C=[[(R[i][j],F(0)) if i!=j else (F(1,2),F(0)) for j in range(n)] for i in range(n)]
        assert all(normsq(x)<=1 for row in C for x in row)
        observed_R=[[F(0) if i==j else (abs(C[i][j][0])+abs(C[j][i][0]))/2 for j in range(n)] for i in range(n)]
        assert R==observed_R
        u=[[((eta+mu)*R[i][j]-mu)/gamma for j in range(n)] for i in range(n)]
        assert all(-mu/gamma<=x<=eta/gamma for row in u for x in row)
        for i in range(n):
            assert u[i][i]==-mu/gamma
            row=sum((max(F(0),u[i][j]) for j in range(n) if i!=j),F(0))
            assert row<=(n-1)*eta/gamma
            tight_rows+=int(row==(n-1)*eta/gamma)
            assert all(u[i][j]==u[j][i] for j in range(n))
        matrix_count+=1
    assert normsq(step(F(2),ONE,NEGONE))==9
    assert normsq(step(F(-1),ONE,NEGONE))==9
    assert normsq(step(F(1,2),ZERO,(F(4),F(0))))==4
    forced=gsub(step(F(1,2),ZERO,ONE),step(F(1,2),ZERO,NEGONE));assert forced==ONE
    mean_of_norms=F(1);norm_of_mean=F(0);assert mean_of_norms!=norm_of_mean
    complex_diag=step(F(1,2),ZERO,ONE);assert complex_diag==(F(1,2),F(0)) and complex_diag!=ZERO
    retained=ZERO
    for _ in range(16):retained=step(F(1),retained,ONE);assert retained==ZERO
    assert normsq(NEGONE)==1 and step(F(1,2),NEGONE,NEGONE)==NEGONE
    # A coarse global range is not itself the sharp lower-band ON certificate.
    c=F(19,30);eps=F(1,10**12);h=F(3,20000);L=F(8,3);S=11*L
    M=(1-h)*c+h*S;kappa=min(F(1),c/(M+eps));share=kappa*h*L/(1-kappa*(1-h))
    assert 0<kappa<=1 and share<F(3,25)
    return [
        {'case':'exact_shared_input_paths','kind':'positive_exact','control_passed':True,'trajectories':64,'updates_each':16,'disk_checks':disk_checks,'difference_checks':difference_checks},
        {'case':'exact_fixed_input_paths','kind':'positive_exact','control_passed':True,'trajectories':64,'updates_each':16,'closed_form_checks':fixed_checks},
        {'case':'exact_reported_drive_matrices','kind':'positive_exact','control_passed':True,'matrices':matrix_count,'tight_row_bounds':tight_rows,'N_values':nodes,'coarse_default_ON_comparison_point':str(share),'threshold':'3/25','coarse_range_alone_not_ON_certificate':True},
        {'case':'exact_adversarial_witnesses','kind':'exact_counterexample','control_passed':True,'witnesses':{
            'drop_alpha_upper_norm_squared':'9','drop_alpha_lower_norm_squared':'9','drop_input_bound_norm_squared':'4',
            'different_input_nonzero_next_difference':'1','mean_of_norms_vs_norm_of_mean':['1','0'],
            'complex_diagonal_vs_reported_diagonal':['1/2','0'],'alpha_one_retains_initial':'0 for every recurrence step',
            'antiphase_unit_magnitude_vs_cosine':['1','-1']}}]


def optimization_control():
    run=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve()),'--assertions-only'],
        text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=20)
    return {'case':'python_optimization_mode','kind':'policy_negative','control_passed':
        run.returncode==2 and 'assertions must be enabled' in run.stdout,
        'raw_python_exit':run.returncode,'observed_output':run.stdout.strip()}


def cases():
    header='import CoherenceEMA\nopen Researcher040282.EMA\n'
    false=[
      ('false_disk_without_alpha_upper','''example : (emaStep 2 1 (-1)).re ≤ 1 := by
  norm_num [emaStep]
'''),
      ('false_disk_without_alpha_lower','''example : -(emaStep (-1) 1 (-1)).re ≤ 1 := by
  norm_num [emaStep]
'''),
      ('false_disk_without_input_bound','''example : (emaStep (1/2) 0 4).re ≤ 1 := by
  norm_num [emaStep]
'''),
      ('false_unforced_difference','''example : (emaStep (1/2) 0 1 - emaStep (1/2) 0 (-1)).re = 0 := by
  norm_num [emaStep]
'''),
      ('false_complex_average_readout','''example : reportedR (fun i j : Fin 2 => if i=j then 0 else if i=0 then 1 else -1) 0 1 = 0 := by
  norm_num [reportedR]
'''),
      ('false_complex_zero_diagonal','''example : (coherenceUpdate (1/2) (fun _ _ : Fin 1 => 0) (fun _ => 0)
    (fun _ => 0) (fun _ => 0) 1 0 0).re = 0 := by
  norm_num [coherenceUpdate, phaseInput, emaStep]
'''),
      ('false_strict_decay_at_alpha_one','''example : ‖emaTrajectory 1 0 (fun _ => 1) 8 - 1‖ < 1 := by
  norm_num [emaTrajectory, emaStep]
'''),
      ('false_coherence_equals_cosine','''example : reportedR (fun _ _ : Fin 2 => (-1 : ℂ)) 0 1 = (-1 : ℝ) := by
  norm_num [reportedR]
''')]
    result=[(name,header+source,'false_math') for name,source in false]
    result += [
      ('sorry_payload',header+'''theorem falseWithEMAHole : (0 : ℚ) = 1 := by sorry
#print axioms falseWithEMAHole
''','sorry_payload'),
      ('extra_axiom_payload',header+'''axiom injectedEMAEquality : (0 : ℚ) = 1
theorem falseWithEMAAxiom : (0 : ℚ) = 1 := injectedEMAEquality
#print axioms falseWithEMAAxiom
''','extra_axiom_payload'),
      ('missing_footprint',header+'''theorem footprintProbe : (0 : ℚ) = 0 := by norm_num
''','missing_footprint')]
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--exact-only',action='store_true');args=parser.parse_args()
    started=time.perf_counter()
    if args.exact_only:
        controls=exact_controls()+[optimization_control()]
        result={'agent':'Researcher 040282','cycle':4,'scope':'exact finite/policy controls only; no Lean invocation',
            'control_count':len(controls),'all_controls_passed':all(c['control_passed'] for c in controls),'controls':controls}
        (ROOT/'exact_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
        return 0 if result['all_controls_passed'] else 1
    (ROOT/'cycle_results.json').unlink(missing_ok=True)
    assert LEAN.is_file() and LAKE.is_file() and (MATHLIB/'lakefile.lean').is_file()
    version=subprocess.check_output([str(LEAN),'--version'],cwd=MATHLIB,text=True).strip()
    assert 'version 4.33.1,' in version
    revision=subprocess.check_output(['git','-C',str(MATHLIB),'rev-parse','HEAD'],text=True).strip();assert revision==REVISION
    sources={name:(ROOT/name).read_text() for name in FILES}
    base=os.environ.copy();base['PATH']=str(LEAN.parent)+os.pathsep+base.get('PATH','')
    env=json.loads(subprocess.check_output([str(LAKE),'env','python','-c',
        'import json,os; print(json.dumps(dict(os.environ)))'],cwd=MATHLIB,env=base,text=True))
    CACHE.mkdir(parents=True,exist_ok=True);LOGS.mkdir(exist_ok=True);builds=[];controls=[]
    print('Fresh reused dependency and new component/bridge builds, then isolated controls.',flush=True)
    with tempfile.TemporaryDirectory(prefix='r040282-c004-dependencies-',dir=CACHE) as tmp:
        dependencies=Path(tmp);dep_env=env.copy();dep_env['LEAN_PATH']=str(dependencies)+os.pathsep+env.get('LEAN_PATH','')
        for filename in FILES:
            name=Path(filename).stem;run,seconds=compile_one(name,sources[filename],dependencies,dep_env)
            checked=assess(sources[filename],run.returncode,run.stdout)
            row={'module':name,'raw_lean_exit':run.returncode,'seconds':seconds,**checked}
            if not checked['verified']:print(run.stdout,flush=True);raise RuntimeError('Positive module rejected: '+name)
            if name in ['CoherenceEMA','CoherenceDriveBridge']:
                controls.append({'case':'positive_'+name,'kind':'positive','control_passed':True,**row})
            else:builds.append(row)
            print(name,'PASS','declarations',checked['declaration_count'],flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            controls+=list(pool.map(lambda item:compile_case(item,dependencies,env),cases()))
    controls+=exact_controls()+[optimization_control()]
    for c in controls:print(c['case'],'PASS' if c['control_passed'] else 'FAIL','raw_lean_exit='+str(c.get('raw_lean_exit','not applicable')),flush=True)
    result={'agent':'Researcher 040282','cycle':4,'compiler_version':version,'mathlib_revision':revision,
        'source_files':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in sources.items()},
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'dependency_builds':builds,'controls':controls,'control_count':len(controls),
        'all_controls_passed':all(c['control_passed'] for c in controls),'elapsed_seconds':time.perf_counter()-started}
    (ROOT/'cycle_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('All controls passed:',result['all_controls_passed'],flush=True)
    return 0 if result['all_controls_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
```

## Appendix G — Complete optional actual-source component checker

<!-- FILE: compare_source.py -->
```python
"""Finite actual-compute_R comparisons; no patched coherence function or coupled run.
Protocol: SOURCE_COMPARISON_PLAN.md. Run with assertions enabled.
"""
from __future__ import annotations
import sys
if not __debug__:
    raise SystemExit('Python assertions must be enabled; do not use -O/-OO.')
import cmath
from dataclasses import replace
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
SOURCE=Path(os.environ.get('R040282_AIEFS_ENGINE',ROOT/'source_state/main/aief_experiment_engine_v1.py')).expanduser().resolve()
ATOL=2e-14
SEED=2026090404


def load_source():
    spec=importlib.util.spec_from_file_location('r040282_ema_engine',SOURCE)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module


def readout(C):
    n=len(C);R=np.zeros((n,n),dtype=float)
    for i in range(n):
        for j in range(n):
            if i!=j:R[i,j]=(abs(complex(C[i,j]))+abs(complex(C[j,i])))/2
    return R


def oracle(C,theta,delayed,cfg,mode=None):
    n=len(theta);result=np.empty((n,n),dtype=complex);alpha=cfg.alpha
    for i in range(n):
        for j in range(n):
            phase=float(theta[i])-float(delayed[j])
            if mode!='omit_omega_tau':phase-=(float(cfg.omega[i])+float(cfg.omega[j]))/2*cfg.tau
            z=cmath.rect(1.0,phase)
            a,b=(1-alpha,alpha) if mode=='swapped_alpha_weights' else (alpha,1-alpha)
            result[i,j]=a*complex(C[i,j])+b*z
    R=readout(result)
    if mode=='old_R_before_update':R=readout(C)
    if mode=='magnitude_after_complex_average':
        for i in range(n):
            for j in range(n):
                if i!=j:R[i,j]=abs((complex(result[i,j])+complex(result[j,i]))/2)
    if mode=='zero_complex_diagonal':np.fill_diagonal(result,0)
    return result,R


def make_state(module,cfg,theta,delayed,C):
    history=[np.array(delayed,dtype=float).copy() for _ in range(cfg.delay_steps+1)]
    history[-1]=np.array(theta,dtype=float).copy()
    return module.DynamicState(theta=np.array(theta,dtype=float).copy(),B=np.zeros((cfg.N,cfg.N)),
        coherence_acc=np.array(C,dtype=complex).copy(),history=history)


def evaluate(module,name,cfg,theta,delayed,C,calls,closed_form=False):
    cfg.validate();state=make_state(module,cfg,theta,delayed,C)
    saved_theta=state.theta.copy();saved_B=state.B.copy();saved_history=[x.copy() for x in state.history]
    reference=state.coherence_acc;expected=np.array(C,dtype=complex).copy()
    c_error=0.;r_error=0.;formula_error=0.;max_c=0.;max_r=0.
    for count in range(1,calls+1):
        expected,expected_R=oracle(expected,theta,saved_history[0],cfg)
        observed=module.compute_R(state,cfg)
        ce=float(np.max(np.abs(state.coherence_acc-expected)));re=float(np.max(np.abs(observed-expected_R)))
        c_error=max(c_error,ce);r_error=max(r_error,re)
        assert ce<=ATOL and re<=ATOL,(name,count,ce,re)
        assert state.coherence_acc is reference
        assert np.array_equal(observed,observed.T) and np.all(np.diag(observed)==0)
        assert np.array_equal(state.theta,saved_theta) and np.array_equal(state.B,saved_B)
        assert all(np.array_equal(x,y) for x,y in zip(state.history,saved_history)) and len(state.history)==len(saved_history)
        max_c=max(max_c,float(np.max(np.abs(state.coherence_acc))));max_r=max(max_r,float(np.max(observed)))
        assert float(np.min(observed))>=0 and max_c<=1+ATOL and max_r<=1+ATOL
        if closed_form:
            off=observed[~np.eye(cfg.N,dtype=bool)]
            fe=float(np.max(np.abs(off-(1-cfg.alpha**count))))
            formula_error=max(formula_error,fe);assert fe<=ATOL,(name,count,fe)
    return {'case':name,'N':cfg.N,'alpha':cfg.alpha,'calls':calls,'maximum_C_error':c_error,
        'maximum_R_error':r_error,'maximum_fixed_input_formula_error':formula_error,
        'maximum_C_norm':max_c,'maximum_R':max_r,'all_passed':True}


def main():
    destination=ROOT/'source_comparison_results.json';destination.unlink(missing_ok=True)
    module=load_source();base=module.DEFAULT_MODEL_CONFIG;rng=np.random.default_rng(SEED)
    cases=[];control_input=None
    for n in [1,2,3,6,12]:
        for rho in [.5,1.,2.]:
            cfg=replace(base,N=n,omega=tuple(float(x) for x in np.linspace(1.,2.,n)),T_window=rho*base.T_window)
            for initial in ['zero','random']:
                theta=rng.uniform(0,2*math.pi,n);delayed=rng.uniform(0,2*math.pi,n)
                C=np.zeros((n,n),dtype=complex) if initial=='zero' else rng.random((n,n))*np.exp(1j*rng.uniform(-math.pi,math.pi,(n,n)))
                name=f'N{n}_rho{rho:g}_{initial}'
                cases.append(evaluate(module,name,cfg,theta,delayed,C,2))
                if n==3 and rho==1 and initial=='random':control_input=(cfg,theta.copy(),delayed.copy(),C.copy())
    for label,offset in [('aligned',0.),('quarter_turn',math.pi/2),('anti_phase',math.pi)]:
        cfg=replace(base,N=2,omega=(1.,1.),T_window=base.dt/math.log(2))
        theta=np.array([0.,offset]);delayed=np.mod(theta-cfg.tau,2*math.pi)
        cases.append(evaluate(module,'fixed_offset_'+label,cfg,theta,delayed,np.zeros((2,2),complex),64,True))
    configuration_controls=[]
    for label,Tw in [('alpha_rounds_to_one',1e30),('alpha_underflows_to_zero',1e-30)]:
        cfg=replace(base,N=2,omega=(1.,1.),T_window=Tw)
        if label=='alpha_underflows_to_zero':
            # Protocol correction is recorded, not silently counted as a numerical pass.
            try:cfg.validate()
            except ValueError as exc:
                assert cfg.alpha==0 and 'alpha=' in str(exc) and '(0, 1]' in str(exc)
                configuration_controls.append({'case':label,'expected_rejection_observed':True,'reason':str(exc),'compute_R_called':False})
            else:raise AssertionError('Expected alpha=0 configuration rejection')
            continue
        theta=np.array([.2,1.4]);delayed=np.array([1.1,.3])
        case=evaluate(module,label,cfg,theta,delayed,np.zeros((2,2),complex),1)
        assert cfg.alpha==1.
        case['interpretation']='Valid binary alpha=1, not a defect; exact-real strict-alpha theorem does not transfer to every binary config.'
        cases.append(case)
    assert control_input is not None
    cfg,theta,delayed,C=control_input;expected_C,expected_R=oracle(C,theta,delayed,cfg)
    sensitivities=[]
    for mode in ['last_history_instead_of_oldest','omit_omega_tau','swapped_alpha_weights','old_R_before_update','magnitude_after_complex_average','zero_complex_diagonal']:
        if mode=='last_history_instead_of_oldest':wrong_C,wrong_R=oracle(C,theta,theta,cfg)
        else:wrong_C,wrong_R=oracle(C,theta,delayed,cfg,mode)
        distance=max(float(np.max(np.abs(wrong_C-expected_C))),float(np.max(np.abs(wrong_R-expected_R))))
        assert distance>1e-8,(mode,distance)
        sensitivities.append({'wrong_translation':mode,'maximum_separation':distance,'detected':True})
    assert len(cases)==34 and len(sensitivities)==6 and len(configuration_controls)==1 and sum(c['calls'] for c in cases)==253
    result={'agent':'Researcher 040282','cycle':4,'scope':'Finite component comparisons of actual compute_R on controlled/clamped states; no advance_state or coupled-trajectory theorem',
        'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seed':SEED,
        'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
        'absolute_tolerance':ATOL,'relative_tolerance':0,'case_count':len(cases),'compute_R_calls':sum(c['calls'] for c in cases),
        'maximum_C_error':max(c['maximum_C_error'] for c in cases),'maximum_R_error':max(c['maximum_R_error'] for c in cases),
        'all_passed':True,'cases':cases,'sensitivity_controls':sensitivities,'configuration_controls':configuration_controls}
    destination.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
```
