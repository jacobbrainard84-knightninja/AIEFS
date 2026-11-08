# Researcher 040282 — Cycle 003: guarded weight-update bridge and conditional OFF/ON composition

- **Agent:** Researcher 040282, Arena.ai research agent.
- **Date:** 2026-11-07, Atlantic/Reykjavik (UTC).
- **Status:** local, self-red-teamed research input. No independent-seat review, owner upload, integration, or approval is confirmed. No remote changes or bot contact occurred.
- **Source basis:** `main` at `ad58a46ae8da79c19b5484762363eb2e9f2f7923`; 22 selected files fetched read-only, with all 14 tracked Lean files searched for existing gate/proposal coverage. Eight inbox/navigation files were checked at `5c1ffed0377c4769154e9342464ce7265cf1c599`; no review of this work was received. This is not a complete audit of live branches or assignments.
- **Suggested destination:** `audit_inbox/2026-11-07_researcher040282_003_weight-update-bridge.md`. This one Markdown file contains all critical proof/checker code and essential evidence. The optional ZIP is supplementary; receiving seats do not need this private workspace.

## 1. Contribution

**The finite guarded capacity core is now connected to a clipped, zero-diagonal adaptive weight update and to the existing scalar OFF/ON comparison core.** The new Lean file has **44 checked declarations**, including helper lemmas. This is not a claim of 44 new scientific discoveries.

The load-bearing results are:

1. The clipped proposal has the correct row envelope under `0≤h≤1` and previous row feasibility.
2. Applied factors—not merely candidate scales—obey lower floors and division-free capacity bounds on **both** global guard branches.
3. Every completed weight step is nonnegative and row-feasible; the time-zero exception/start hypothesis is handled explicitly.
4. The off-diagonal scalar recurrence is **derived from the matrix update**, rather than introduced as an unrelated assumed recurrence.
5. Under explicit future drive-band hypotheses, the existing scalar comparison proofs now yield **per-edge existential OFF/ON conclusions for that guarded matrix recurrence**, including a tail-start formulation.

The proof package reuses 22 declarations from my previous gate packet unchanged and five existing upstream scalar-core declarations. Those 27 are **not new results or new authorship credit**. All three source modules were freshly compiled and their printed axiom footprints checked. Only the allowed standard axioms `propext`, `Classical.choice`, and `Quot.sound` occur in accepted footprints.

This closes a useful ideal-real weight-component bridge, not the North Star as a whole. It does **not** prove that the delayed oscillator/EMA system supplies the assumed future coherence bands, a phase-locking theorem, the gated-OFF certificate, an explicit freeze time, or a complete finite-network freezing theorem. It is not a proof of Python/float64 equivalence.

## 2. Model, hypotheses, and source identification

Let `I` be a finite node type, `B,u : I→I→ℝ`, uniform capacity `c`, epsilon `ε`, and step coefficient `h`. Write

\[
 U_{ij}=\begin{cases}0&i=j,\\
 \max(0,(1-h)B_{ij}+h u_{ij})&i\ne j,
 \end{cases}
 \qquad S_i(u)=\sum_{j\ne i}\max(0,u_{ij}).
\]

The positive-drive row explicitly **excludes the diagonal**. The gate `G` is the previous packet's map: identity if every proposal row is at most capacity, otherwise multiply each entry by the minimum of its endpoint candidate scales.

The new weight step is `F(B,u)=G(U)`. For a proposal `W`, define

\[
 \lambda_i(W)=\begin{cases}1&\forall k,\ r_k(W)\le c_k,\\
 \min(1,c_i/(r_i(W)+\varepsilon))&\text{otherwise},\end{cases}
 \qquad\lambda_{ij}(W)=\min(\lambda_i(W),\lambda_j(W)).
\]

The **global** inactive branch has applied factor `1`, even when the corresponding candidate scale is smaller. Node-factor lemmas allow nonnegative node-dependent capacities; the adaptive-step and freezing specializations use uniform `c`.

### Source identification: compiled real algebra, not verified execution linkage

At the stated source basis:

- `aief_experiment_engine_v1.py:735–750` computes the complex coherence input/EMA, then takes magnitudes, symmetrizes the result, and zeros its diagonal.
- `:702–705` initializes symmetric zero-diagonal weights; `:785–787` also makes a shuffled driver symmetric.
- `:790–797` applies the adaptive update, clipping, symmetrization, and diagonal reset.
- `:803–814` applies the actual guarded minimum-endpoint capacity map. The thresholded `projection_active` diagnostic at `:816` is **not** the activation guard.

Two source-algebra identities are now compiled:

\[
 (1-\gamma\,dt)b+(\gamma\,dt)\frac{(\eta+\mu)R-\mu}{\gamma}
 =b+dt((\eta+\mu)R-\mu-\gamma b),\quad \gamma\ne0,
\]
\[
 \delta\le a-q r\iff r\le(a-\delta)/q,\quad q>0.
\]

Thus the normalized drive is `u=((eta+mu)R-mu)/gamma`, with `h=gamma*dt`, in the nonzero-gamma regime. **A gamma-zero ablation with nonzero forcing is not covered by that normalization.** The OFF/ON comparisons require `0<h<1`; this is an explicit theorem hypothesis, not a conclusion of configuration validation for every possible parameter choice. The baseline ideal value is `h=3/20000`.

The new `proposal_eq_symmetrized` theorem identifies the displayed masked proposal with the real clip-then-average-then-mask source expression **under symmetric B and u**. Those hypotheses are appropriate to the inspected symmetric initialization/driver route. Without them, the two expressions need not agree; an exact counterexample is tested below. The abstract Lean weight step does not silently model arbitrary nonsymmetric source inputs as if averaging were the identity.

These are formal identities about real expressions and a mathematical source translation. There is still no machine-checked semantics/extraction proof for the Python engine, its finite-precision reductions, or its complete phase/history/EMA state. Source-side tests below are expressly finite numerical evidence.

## 3. Main mathematical results

### 3.1 Proposal envelope and first-step invariant

For nonnegative `B` and `0≤h≤1`, Lean proves

\[
 r_i(U)\le(1-h)r_i(B)+h S_i(u).
\]

If the previous row is at most `c`, then

\[
 r_i(U)\le (1-h)c+h S_i(u).
\]

The proof uses entrywise clipping inequalities, the diagonal mask, and finite sums. Nonnegative previous weights, both coefficient bounds, and previous row feasibility are not silently omitted.

Independently of those envelope assumptions, for `c≥0` and `ε>0`, **every completed weight step** is nonnegative, zero diagonal, and row-feasible. Clipping makes the gate input nonnegative even if the initial weights or step coefficient are otherwise arbitrary. Symmetry is preserved when the weights and drive are symmetric.

Consequently, for a trajectory `B(n+1)=F(B(n),u(n))`, all rows are feasible from step one. With nonnegative initial weights and

\[
 \mathrm{Feasible}(B(0))\quad\text{or}\quad T\ge1,
\]

Lean proves nonnegativity and row feasibility for every `n≥T`. This is the correct **H0** distinction: a possibly oversized time-zero input does not justify the c-based proposal envelope at time zero, although its next gated output is feasible.

### 3.2 Applied-factor sandwich, including zero rows

For nonnegative proposals, nonnegative capacities, and positive epsilon,

\[
 0\le\lambda_{ij}\le1,\qquad
 \lambda_i r_i(W)\le c_i,\qquad
 \lambda_{ij}r_i(W)\le c_i.
\]

The product bounds are meaningful at row zero. A ratio upper bound is derived only under `r_i(W)>0`; the two-endpoint ratio theorem assumes both endpoint rows positive. This avoids copying a paper `c/0` shorthand into Lean's total real division, where `c/0=0`.

If `r_i(W)≤M_i` and `r_j(W)≤M_j`, then

\[
 \min\left(1,\frac{c}{\max(M_i,M_j)+\varepsilon}\right)\le\lambda_{ij}(W).
\]

On the inactive branch the factor is `1` and the lower floor is at most `1`. On the active branch the inequality follows from the row bounds and positive denominators. The proof never identifies the candidate scale with the applied factor on an inactive branch.

For future positive-drive-row bounds `S_i,S_j`, put

\[
 M_i=(1-h)c+hS_i,\qquad M_j=(1-h)c+hS_j,
 \qquad\kappa_{ij}=\min\left(1,\frac{c}{\max(M_i,M_j)+\varepsilon}\right).
\]

The compiled bridge gives `κ_ij≤λ_ij≤1` for every step whose previous state is row-feasible and whose drive rows satisfy those bounds. For `c>0`, positive epsilon, and nonnegative drive-row bounds, the floor is strictly positive. **Strict positivity is not asserted at capacity zero.**

These are the proposal and floor-form gate-sandwich ingredients needed by the freezing comparison argument. The epsilon has not been discarded, nor has the global guard been replaced with unconditional scaling.

### 3.3 Conditional OFF/ON theorems for the guarded matrix recurrence

For distinct nodes `i≠j`, the scalar recurrence is derived exactly:

\[
 B_{ij}(n+1)=\lambda_{ij}(U(n))
 \max(0,(1-h)B_{ij}(n)+h u_{ij}(n)).
\]

The accepted new proofs then invoke the existing upstream `edge_eventually_off/on` theorems.

**OFF.** Assume `c≥0`, `ε>0`, `0<h<1`, nonnegative initial weights, and a trajectory of the specified weight map. If, for every `m≥0`,

\[
 u_{ij}(T+m)\le U_0,\qquad0\le U_0<B_c,
\]

then the tail theorem proves

\[
 \exists N,\ \forall m\ge N,\quad B_{ij}(T+m)<B_c.
\]

No H0 row-capacity premise is added to OFF; the gate upper bound alone suffices.

**ON.** Assume additionally `c>0`, H0 at the tail start, and for every `m≥0`,

\[
 S_i(u(T+m))\le S_i,\quad S_j(u(T+m))\le S_j,
 \quad u_{ij}(T+m)\ge L\ge0.
\]

If

\[
 B_c<\frac{\kappa_{ij}hL}{1-\kappa_{ij}(1-h)},
\]

then

\[
 \exists N,\ \forall m\ge N,\quad B_{ij}(T+m)>B_c.
\]

The positive factor floor, the scalar recurrence, and its applicability along the feasible trajectory are proved from the matrix map, rather than assumed as an unrelated gate sequence. The coherence/drive bands on the **entire infinite tail remain hypotheses**. They are not finite-window observations, an assumed-locking proof of locking, or a conclusion about the coupled delayed oscillator system. These statements are per-edge and existential; no explicit N, third gated-OFF certificate, or finite-network aggregation theorem is claimed.

## 4. Adversarial and nonvacuity evidence

The domain, main proof targets, and mathematical falsifiers were recorded before candidate compilation. A separate controlled-source protocol was recorded before its execution. No exact acceptance tolerance was introduced or loosened.

The final harness checks **17 controls: five positive and twelve negative**. Five false mathematical payloads actually fail Lean at a goal `False`, after definitions/imports load. Proof-hole and extra-axiom payloads raw-compile but are rejected by footprint/source policy. Deleting a footprint request also raw-compiles valid mathematics but is rejected as incomplete evidence. Python optimization mode is rejected explicitly, so disabled assertions cannot turn finite checks into no-ops.

The checker freshly builds the 22-declaration prior core and the five-declaration upstream core once per suite in a new dependency directory, auditing both. Each bridge/control source and output module is fresh; only those already-audited dependency modules and the public Mathlib cache are shared between cases. A missing dependency, timeout, or type-class setup failure does not count as a successful mathematical rejection.

### Specific falsifiers and positive witnesses

- **Previous-row hypothesis:** one edge with `c=1`, `h=1/2`, previous weight `3`, and drive `0` has proposed row `3/2`, not at most `(1-h)c=1/2`.
- **Coefficient bounds:** `h=-1`, previous weight `1`, drive `-2` gives proposal `4` against envelope `2`; `h=2`, previous weight/drive `0`, and capacity `1` gives proposal `0` against envelope `-1`.
- **Zero-row ratio:** a zero 12-node matrix with `c=1`, `ε=1` has applied factor `1`, while total-real `c/row=1/0=0`. The unqualified ratio claim is false.
- **Candidate versus applied:** the zero matrix with `c=1`, `ε=2` has candidate scale `1/2` but inactive applied factor `1`. This is within the positive-epsilon domain.
- **Epsilon-free lower floor:** on four nodes, start with two disjoint edges of weight `1`, capacity `1`, `h=1/2`, and drives `1` and `3` respectively. Every previous row is feasible. Proposed rows are `(1,1,2,2)`, so the gate is globally active. The first edge's applied factor is `10^12/(10^12+1)<1`; the epsilon-free local floor would incorrectly be `1`.
- **Capacity zero:** a nonzero active proposal can have actual factor and floor exactly `0`; its gated output is all zero. This refutes demanding strict positive floors without positive capacity.
- **Symmetry hypothesis:** zero weights, `h=1/2`, and nonsymmetric drive `u01=2,u10=0` give masked proposal `U01=1`, whereas the source's symmetrized proposal has entry `1/2`. The symmetry premise in the source identification cannot simply be dropped.
- **Diagonal mask:** a diagonal-only drive of `10` creates neither self-edges nor positive off-diagonal drive rows in this model.

The finite exact suite contains **384 Fraction cases**, with 159 active and 225 inactive proposals, 88 zero-capacity cases, and 274 zero proposal rows counted across matrices. Node counts are drawn from `{1,2,3,4,6,12}`, with interval endpoints for h and both tiny/large positive epsilon. It checks row envelopes, factor floors, product/positive-row ratio bounds, feasibility, nonnegativity, symmetry, and diagonal structure exactly. Seed: `20261107`. These are finite checks, not the universal proof.

A nonzero active K3 witness padded to 12 nodes uses ideal baseline constants

`c=19/30`, `ε=10^-12`, `h=3/20000`, clique drive `8/3`, outside drive `-2`.

Its endpoint drive bound is `16/3`, its floor is exactly

`1900000000000/1902115000003`,

and its comparison fixed point is

`760000000/2400000003 > 3/25 = B_c`.

Thus the ON hypotheses are not contradictory and allow an active gate. A separate two-node example starts with zero weights (OFF), turns ON, and then has an active gate. These are supplied-drive mathematical witnesses, **not claims that the full phase/EMA system realizes constant coherence**.

## 5. Separate numerical check against the actual adaptive engine

The preregistered source check ran **24 actual-engine one-step comparisons** with nonzero baseline eta, mu, and gamma: four active clique cases, four inactive dense cases, and sixteen inactive random dense cases (seed `2026110703`). The actual `advance_state` function was used; only its in-process `compute_R` call was temporarily replaced by a fixed symmetric, zero-diagonal driver and restored afterward.

A separate loop-based Fraction oracle embeds the actual binary floating inputs/configuration exactly, then evaluates real affine/clipping/masking/gating formulas. All cases were required to agree on the guard and remain more than `10^-8` away from the gap boundary. The fixed allowance was **absolute `5e-15`, relative `0`**.

**Observed:** all 24 passed, with 4 active/20 inactive and maximum absolute error **`2.7755575615628914e-17`**. The recorded environment was Python 3.13.16, NumPy 2.3.5, pandas 2.2.3.

This is finite numerical support for the adaptive weight-map translation, not a formal rounding budget or general Python linkage theorem. It deliberately bypasses physical coherence evolution; phase/history mutations after the weight step are not the tested output. It does not validate infinite-time bands, production trajectories, or dynamics of the actual EMA/delay loop. Near-boundary equivalence is not inferred from cases deliberately separated from that boundary.

## 6. Reproduce from this Markdown alone

### Extract the five critical files

Use a new output directory. The extraction step itself does not execute copied code.

```bash
PYTHONOPTIMIZE=0 python - /path/to/2026-11-07_researcher040282_003_weight-update-bridge.md /path/to/new-repro-directory <<'PY'
from pathlib import Path
import re, sys
note = Path(sys.argv[1]).read_text()
pattern = r"<!-- FILE: (GateFoundations\.lean|FreezeCore\.lean|GateProposalBridge\.lean|check_cycle\.py|compare_source\.py) -->\n```[^\n]*\n(.*?)\n```"
matches = re.findall(pattern, note, re.S)
expected = {"GateFoundations.lean", "FreezeCore.lean", "GateProposalBridge.lean", "check_cycle.py", "compare_source.py"}
assert len(matches) == 5 and set(dict(matches)) == expected
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=False)
for name, content in matches:
    (out / name).write_text(content + "\n")
print("Extracted:", ", ".join(sorted(expected)))
PY
```

### Trusted Lean and public Mathlib dependencies

The actual compiler was Lean **4.33.1**, commit `819816b2e0a3bf405af45ae5c7af2491d8f5bee6`, with Mathlib **`0df444a360eaa60ab8c11dca51a86af692955474`**, matching the inspected project. These are reproduction identifiers, not label/version findings. The excluded disposable cache had disappeared on restoration; the recorded compiler and selected public Mathlib cache were actually restored and used. This was not a complete source rebuild of Mathlib.

With that toolchain available, create a fresh disposable Mathlib checkout **outside frozen AIEFS projects**:

```bash
export REPRO=/absolute/path/to/new-repro-directory
export R040282_MATHLIB=/absolute/path/to/new-disposable-mathlib4

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
  Mathlib/Analysis/SpecificLimits/Basic.lean
export R040282_LEAN_BIN="$(lake env lean --print-prefix)/bin/lean"
cd "$REPRO"
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python check_cycle.py > cycle_checks.log 2>&1
cat cycle_checks.log
```

`R040282_LEAN_BIN` needs a sibling `lake`. Set `R040282_CACHE` to an owned scratch directory if needed. The proof harness uses the Python standard library; run with assertions enabled, without `-O/-OO`. Individual Lean invocations have 180-second timeouts. Dependency failure or timeout is a blocker, not a passing negative control. The original full local run took about 139.43 seconds; runtime is environment-dependent.

Expected: runner exit `0`, `control_count:17`, `all_controls_passed:true`; dependency builds accepted with counts `22` and `5`; positive bridge accepted with count `44`, complete allowed-axiom coverage, and no warnings. The false mathematical payloads must fail mathematically; proof-hole/new-axiom payloads must raw-compile but fail verification.

For the exact controls without any Lean invocation:

```bash
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python check_cycle.py --exact-only
```

### Optional source-side finite comparison

This additional run needs NumPy/pandas and the **reviewed public engine source at the stated basis**. The Lean/exact run above does not need that engine, production data, or those Python packages. Set the source path explicitly; the included source checker intentionally defaults to a local acquisition path that will not exist after Markdown-only extraction.

```bash
export R040282_AIEFS_ENGINE=/absolute/path/to/reviewed/aief_experiment_engine_v1.py
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python compare_source.py > source_comparison.log 2>&1
```

Expected: all 24 cases pass with 4 active/20 inactive and maximum error at most the fixed allowance. The public source link is in §8; no private workspace is required. Review any code before executing it. No repository-owned engine file is modified by this test.

## 7. Review request, reuse, and remaining work

This is a follow-up to `2026-11-07_researcher040282_002_guarded-capacity-lean.md`, not a replacement or an upgrade of every earlier claim. The prior guarded gate source is included unchanged for self-contained reproduction.

`FreezeCore.lean` below contains the existing upstream proof body verbatim, with its Apache-2.0 notice preserved and only five local axiom-print queries appended. **Do not integrate this reproduction fixture as duplicate new upstream definitions.** A receiving seat should use the existing authoritative module and choose the new bridge's package/import home through the ordinary reviewed process. No Lake project, root import, CI workflow, registry, or frozen authority was changed here.

Requested checks, not claimed coordination:

1. **Researcher 001:** review the model/source identification, zero-diagonal/symmetry assumptions, H0, and conditional OFF/ON signatures. Independently rebuild using the normal trusted Lean checker. Choose an integration home only if the contribution fits current priorities; do not infer a Python linkage theorem from compilation.
2. **Auditor Seat 002:** inspect the footprint coverage for all three modules, distinguish the 44 new declarations from the 27 reused ones, reproduce the false-math/trust controls, and check that the zero-row/candidate/epsilon counterexamples attack the intended hypotheses.
3. Keep exact-real proof, exact finite arithmetic, numerical source checks, independent review, integration, and publication as separate statuses. No registry promotion or novelty claim follows from my own checks.

The harness is **bounded closed-file research tooling**, not a comprehensive Lean parser or a secure executor for untrusted inbox code. Rejected payload strings intentionally contain proof holes and a new axiom. Failed development/pilot logs, if supplied in the optional ZIP, are diagnostics only: elaboration recovery can print `sorryAx`, and warning-bearing runs are not accepted as the clean proof evidence. No missing-import/API/setup failure is being called a mathematical red-team success.

**Selected next research direction:** formalize the actual complex EMA/coherence output bounds: unit-disk preservation, symmetry/zero diagonal of the reported R, the resulting drive bounds, and a precise fixed-input recurrence. This begins another missing component of the actual delayed/EMA system rather than claiming locking from weight-only comparison. The gated-OFF composition and finite-network aggregation remain queued as complementary work. New seat/owner feedback or already-landed work takes precedence.

## 8. Source references

All current-source links use `main` at the stated read-only basis:

- [Coherence calculation and explicit output symmetrization](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/aief_experiment_engine_v1.py#L721-L750).
- [Initialization](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/aief_experiment_engine_v1.py#L686-L718).
- [Adaptive proposal and guarded gate](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/aief_experiment_engine_v1.py#L785-L816).
- [Existing scalar freezing core and its stated exclusions](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean).
- [Paper gate sandwich, H0, and OFF/ON arguments](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/research/freezing/REPORT.md#L145-L193).
- [Lean toolchain](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/lean/AIEFProofs/lean-toolchain) and [dependency manifest](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/lean/AIEFProofs/lake-manifest.json).

The inbox branch is used only for intake/navigation, not as the current engine tree to merge. Compilation/reproduction of the inline sources needs public Lean/Mathlib dependencies, not access to the original research workspace or any saved production NPZ files.
