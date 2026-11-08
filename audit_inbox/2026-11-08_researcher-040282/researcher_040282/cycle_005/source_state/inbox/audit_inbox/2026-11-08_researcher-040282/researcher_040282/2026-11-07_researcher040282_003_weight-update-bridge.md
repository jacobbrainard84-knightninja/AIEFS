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

## 9. Actual fresh-build evidence

**Compiler:** `Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)`.

| Module | Credit / role | Checked declarations | Raw Lean exit | Accepted |
|---|---|---:|---:|---|
| GateFoundations | Prior local core, unchanged | 22 | 0 | Yes |
| FreezeCore | Existing upstream core; proof body unchanged | 5 | 0 | Yes |
| GateProposalBridge | New bridge, including helper lemmas | 44 | 0 | Yes |

Each accepted module has complete requested/printed axiom coverage, no compiler warnings/errors, and no footprint outside the allowed standard set. The final local runner exited `0`.

### Control outcomes

| Case | Raw Lean exit | Observed outcome |
|---|---:|---|
| `positive` | 0 | Accepted, 44/44 allowed footprints |
| `false_previous_row_bound` | 1 | Rejected mathematically; no dependency error |
| `false_without_h_lower` | 1 | Rejected mathematically; no dependency error |
| `false_without_h_upper` | 1 | Rejected mathematically; no dependency error |
| `false_zero_row_ratio` | 1 | Rejected mathematically; no dependency error |
| `false_candidate_equals_applied` | 1 | Rejected mathematically; no dependency error |
| `sorry_payload` | 0 | Rejected: `compiler_warning; forbidden_source_token:sorry; unapproved_axioms:falseWithBridgeHole:sorryAx` |
| `extra_axiom_payload` | 0 | Rejected: `forbidden_source_token:axiom; unapproved_axioms:falseWithBridgeAxiom:injectedBridgeEquality` |
| `missing_footprint` | 0 | Rejected: `theorem_axiom_print_coverage` |
| `exact_fraction_suite` | not a Lean case | Exact positive checks passed |
| `nonvacuous_on_active_and_turn_on` | not a Lean case | Exact positive checks passed |
| `inactive_zero_row_witness` | not a Lean case | Exact positive checks passed |
| `drop_epsilon_from_floor` | not a Lean case | Wrong/dropped-hypothesis variant refuted exactly |
| `strict_positive_floor_at_zero_capacity` | not a Lean case | Wrong/dropped-hypothesis variant refuted exactly |
| `drop_symmetry_from_source_identification` | not a Lean case | Wrong/dropped-hypothesis variant refuted exactly |
| `diagonal_mask_witness` | not a Lean case | Exact positive checks passed |
| `python_optimization_mode` | not a Lean case | Optimized Python rejected before assertions can be bypassed (exit 2) |

### Recorded runner output

```text
Fresh dependency builds, then fresh bridge/control sources.
positive PASS raw_lean_exit=0 verified=True
false_previous_row_bound PASS raw_lean_exit=1 verified=False
false_without_h_lower PASS raw_lean_exit=1 verified=False
false_without_h_upper PASS raw_lean_exit=1 verified=False
false_zero_row_ratio PASS raw_lean_exit=1 verified=False
false_candidate_equals_applied PASS raw_lean_exit=1 verified=False
sorry_payload PASS raw_lean_exit=0 verified=False
extra_axiom_payload PASS raw_lean_exit=0 verified=False
missing_footprint PASS raw_lean_exit=0 verified=False
exact_fraction_suite PASS raw_lean_exit=not applicable verified=not applicable
nonvacuous_on_active_and_turn_on PASS raw_lean_exit=not applicable verified=not applicable
inactive_zero_row_witness PASS raw_lean_exit=not applicable verified=not applicable
drop_epsilon_from_floor PASS raw_lean_exit=not applicable verified=not applicable
strict_positive_floor_at_zero_capacity PASS raw_lean_exit=not applicable verified=not applicable
drop_symmetry_from_source_identification PASS raw_lean_exit=not applicable verified=not applicable
diagonal_mask_witness PASS raw_lean_exit=not applicable verified=not applicable
python_optimization_mode PASS raw_lean_exit=not applicable verified=not applicable
All controls passed: True
```

### Complete accepted-module axiom output

**GateFoundations**

```text
'Researcher040282.rowSum_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.nodeScale_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.nodeScale_le_one' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.kernel_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.kernel_le_input' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.kernel_symmetric' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.kernel_zero_diag' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.kernel_row_lower' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.kernel_row_upper' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.kernel_feasible' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.gate_fixes_feasible' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.gate_feasible' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.gate_idempotent' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.gate_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.gate_symmetric' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.gate_zero_diag' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.scale_eq_of_rowSum_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.gate_difference_of_rowSum_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.rat_guard_fixes_boundary' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.rat_kernel_not_idempotent' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.rat_gate_not_nonexpansive' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.rat_negative_epsilon_breaks_capacity' depends on axioms: [propext, Classical.choice, Quot.sound]
```

**FreezeCore**

```text
'AIEFFreeze.upper_geom' depends on axioms: [propext, Classical.choice, Quot.sound]
'AIEFFreeze.eventually_off' depends on axioms: [propext, Classical.choice, Quot.sound]
'AIEFFreeze.eventually_on' depends on axioms: [propext, Classical.choice, Quot.sound]
'AIEFFreeze.edge_eventually_off' depends on axioms: [propext, Classical.choice, Quot.sound]
'AIEFFreeze.edge_eventually_on' depends on axioms: [propext, Classical.choice, Quot.sound]
```

**GateProposalBridge**

```text
'Researcher040282.normalized_affine_identity' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.gap_capacity_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.positiveDrive_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.positiveDriveRow_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.proposal_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.proposal_zero_diag' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.proposal_apply_of_ne' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.proposal_symmetric' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.proposal_eq_symmetrized' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.proposal_entry_upper' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.proposal_row_upper' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.proposal_row_upper_of_feasible' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedFactor_eq_min_appliedNodeScale' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedFactor_comm' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.gate_eq_mul_appliedFactor' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedNodeScale_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedNodeScale_le_one' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedFactor_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedFactor_le_one' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedNodeScale_mul_row_le_capacity' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedFactor_mul_row_le_capacity' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedNodeScale_le_capacity_div_row' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedFactor_le_capacity_div_row' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedFactor_ratio_upper' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.scaleFloor_pos' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.scaleFloor_le_one' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedNodeScale_lower_of_row_upper' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.appliedFactor_lower_of_row_uppers' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.driveEnvelope_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.edgeFloor_pos' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.edgeFloor_le_one' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.weightStep_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.weightStep_feasible' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.weightStep_symmetric' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.weightStep_zero_diag' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.weightStep_scalar_recurrence' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.weightStep_factor_lower_of_drive_bounds' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.trajectory_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.trajectory_feasible_from_first' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.trajectory_good_of_start' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.adaptive_edge_eventually_off' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.adaptive_edge_eventually_on' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.adaptive_edge_eventually_on_from' depends on axioms: [propext, Classical.choice, Quot.sound]
'Researcher040282.adaptive_edge_eventually_off_from' depends on axioms: [propext, Classical.choice, Quot.sound]
```

### Single-Markdown reproduction was also executed

All five critical files below were extracted from this standalone Markdown into a fresh directory. The extracted proof checker freshly rebuilt its two dependency modules and ran all 17 controls: exit `0`, all intended outcomes repeated. The extracted source checker was also run with the reviewed public engine as an explicit external dependency: exit `0`, all 24 comparisons passed again. The extracted code matches the final supplied code exactly. **This is local self-reproduction, not independent-seat review.**

## Appendix A — Prior local core, unchanged

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

## Appendix B — Upstream scalar comparison core; only audit queries appended

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

## Appendix C — Complete new bridge

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

## Appendix D — Complete bounded proof/exact checker

<!-- FILE: check_cycle.py -->
```python
"""Fresh guarded-weight bridge builds and bounded adversarial controls.

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
FILES=['GateFoundations.lean','FreezeCore.lean','GateProposalBridge.lean']
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
    with tempfile.TemporaryDirectory(prefix='r040282-c003-'+name+'-',dir=CACHE) as tmp:
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


def rows(w):return [sum(row,F(0)) for row in w]
def zeros(n):return [[F(0) for _ in range(n)] for _ in range(n)]
def positive_rows(u):return [sum((max(F(0),x) for j,x in enumerate(row) if i!=j),F(0)) for i,row in enumerate(u)]
def propose(h,b,u):
    return [[F(0) if i==j else max(F(0),(1-h)*b[i][j]+h*u[i][j])
        for j in range(len(b))] for i in range(len(b))]
def gate_info(c,eps,w):
    rs=rows(w);candidate=[min(F(1),c/(r+eps)) for r in rs];active=any(r>c for r in rs)
    applied=candidate if active else [F(1)]*len(w)
    result=[[w[i][j]*min(applied[i],applied[j]) for j in range(len(w))] for i in range(len(w))]
    return result,applied,candidate,active

def floor(c,eps,m):return min(F(1),c/(m+eps))
def envelope(c,h,s):return (1-h)*c+h*s

def exact_controls():
    rng=random.Random(20261107);counts={'cases':384,'active':0,'inactive':0,'capacity_zero':0,'zero_rows':0}
    for case in range(counts['cases']):
        n=rng.choice([1,2,3,4,6,12]);c=rng.choice([F(0),F(19,30),F(1),F(3)])
        h=rng.choice([F(0),F(1,10),F(1,2),F(1)]);eps=rng.choice([F(1,10**12),F(1,10),F(2)])
        b=zeros(n);u=zeros(n)
        for i in range(n):
            u[i][i]=F(rng.randint(-20,20),6)
            for j in range(i):
                b[i][j]=b[j][i]=F(rng.randint(0,20),20)
                u[i][j]=u[j][i]=F(rng.randint(-20,20),6)
        factor=c/(1+max(rows(b),default=F(0)))
        b=[[x*factor for x in row] for row in b]
        assert all(r<=c for r in rows(b))
        p=propose(h,b,u);sp=positive_rows(u);ms=[envelope(c,h,s) for s in sp]
        out,applied,_,active=gate_info(c,eps,p)
        counts['active' if active else 'inactive']+=1;counts['capacity_zero']+=int(c==0)
        counts['zero_rows']+=sum(r==0 for r in rows(p))
        assert all(x>=0 for row in out for x in row) and all(r<=c for r in rows(out))
        assert all(out[i][i]==0 for i in range(n))
        assert all(out[i][j]==out[j][i] for i in range(n) for j in range(n))
        for i,r in enumerate(rows(p)):
            assert r<=(1-h)*rows(b)[i]+h*sp[i]<=ms[i]
            assert 0<=applied[i]<=1 and applied[i]*r<=c
            if r>0:assert applied[i]<=c/r
            assert floor(c,eps,ms[i])<=applied[i]
            for j in range(n):
                kappa=floor(c,eps,max(ms[i],ms[j]))
                assert 0<=kappa<=min(applied[i],applied[j])<=1
                if c>0:assert kappa>0
    assert counts['active']>0 and counts['inactive']>0 and counts['capacity_zero']>0 and counts['zero_rows']>0
    # Configured exact-rational constants, K3 padded to twelve nodes.
    c=F(19,30);eps=F(1,10**12);h=F(3,20000);b=zeros(12);u=[[F(-2)]*12 for _ in range(12)]
    for i in range(3):
        for j in range(i):b[i][j]=b[j][i]=c/2;u[i][j]=u[j][i]=F(8,3)
    p=propose(h,b,u);out,app,_,active=gate_info(c,eps,p);s=positive_rows(u)[0]
    kappa=floor(c,eps,envelope(c,h,s));share=kappa*h*F(8,3)/(1-kappa*(1-h));bc=F(3,25)
    assert all(r<=c for r in rows(b)) and active and out[0][1]>0
    assert 0<kappa<=app[0]<=1 and 1-kappa*(1-h)>0 and share>bc
    default_witness={'c':str(c),'epsilon':str(eps),'h':str(h),'endpoint_drive_bound':str(s),
        'kappa':str(kappa),'comparison_fixed_point':str(share),'threshold':str(bc),
        'proposal_row_0':str(rows(p)[0]),'output_row_0':str(rows(out)[0]),'active':active}
    # A distinct initial-OFF example turns ON, then uses an active gate.
    b=zeros(2);u=[[F(0),F(2)],[F(2),F(0)]];statuses=[False];active_steps=[]
    for _ in range(4):
        b,_,_,act=gate_info(F(1),eps,propose(F(1,2),b,u))
        statuses.append(b[0][1]>F(1,2));active_steps.append(act)
    assert statuses[1:] == [True]*4 and active_steps[0] is False and active_steps[1] is True
    # Inactive all-zero input: c=1, epsilon=2, applied=1 but candidate=1/2.
    z=zeros(12);_,app,can,act=gate_info(F(1),F(2),z)
    assert not act and app[0]==1 and can[0]==F(1,2)
    # Dropping epsilon defeats the floor on a globally active, valid proposal.
    b=zeros(4);u=zeros(4)
    for i,j,x in [(0,1,F(1)),(2,3,F(1))]:b[i][j]=b[j][i]=x
    u[0][1]=u[1][0]=F(1);u[2][3]=u[3][2]=F(3)
    p=propose(F(1,2),b,u);_,app,_,act=gate_info(F(1),eps,p)
    assert all(r<=1 for r in rows(b)) and rows(p)[0]==1 and act
    assert app[0]==floor(F(1),eps,F(1))<floor(F(1),F(0),F(1))==1
    epsilon_witness={'actual_local_factor':str(app[0]),'epsilon_free_floor':'1','previous_rows':[str(r) for r in rows(b)],'proposal_rows':[str(r) for r in rows(p)]}
    # Strictly positive factor floors cannot be demanded at capacity zero.
    b=zeros(2);u=[[F(0),F(1)],[F(1),F(0)]];p=propose(F(1,2),b,u)
    out,app,_,act=gate_info(F(0),eps,p)
    assert act and app[0]==0 and all(x==0 for row in out for x in row)
    assert floor(F(0),eps,envelope(F(0),F(1,2),F(1)))==0
    # Real symmetrization is not the identity without the drive symmetry premise.
    b=zeros(2);u=[[F(0),F(2)],[F(0),F(0)]];p=propose(F(1,2),b,u)
    sym=[[F(0) if i==j else (p[i][j]+p[j][i])/2 for j in range(2)] for i in range(2)]
    assert p[0][1]==1 and sym[0][1]==F(1,2) and p!=sym
    # A diagonal-only positive forcing must not create self-edges or drive rows.
    b=zeros(3);u=zeros(3)
    for i in range(3):u[i][i]=F(10)
    p=propose(F(1,2),b,u)
    assert p==zeros(3) and positive_rows(u)==[F(0)]*3
    return [
      {'case':'exact_fraction_suite','kind':'positive_exact','control_passed':True,**counts},
      {'case':'nonvacuous_on_active_and_turn_on','kind':'positive_exact','control_passed':True,'default_active_witness':default_witness,'from_empty_statuses':statuses,'from_empty_active_steps':active_steps},
      {'case':'inactive_zero_row_witness','kind':'positive_exact','control_passed':True,'applied_factor':'1','candidate_scale':'1/2'},
      {'case':'drop_epsilon_from_floor','kind':'exact_counterexample','control_passed':True,**epsilon_witness},
      {'case':'strict_positive_floor_at_zero_capacity','kind':'exact_counterexample','control_passed':True,'actual_factor':'0','floor':'0','output_all_zero':True},
      {'case':'drop_symmetry_from_source_identification','kind':'exact_counterexample','control_passed':True,'masked_proposal_01':'1','symmetrized_source_01':'1/2'},
      {'case':'diagonal_mask_witness','kind':'positive_exact','control_passed':True,'diagonal_drive':'10','proposal_all_zero':True,'positive_drive_rows_all_zero':True}]


def optimization_control():
    run=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve()),'--assertions-only'],
        text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=20)
    return {'case':'python_optimization_mode','kind':'policy_negative','control_passed':
        run.returncode==2 and 'assertions must be enabled' in run.stdout,
        'raw_python_exit':run.returncode,'observed_output':run.stdout.strip()}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--exact-only',action='store_true');args=parser.parse_args()
    started=time.perf_counter()
    if args.exact_only:
        controls=exact_controls()+[optimization_control()]
        result={'agent':'Researcher 040282','cycle':3,'scope':'exact controls only; no Lean invocation',
            'all_controls_passed':all(r['control_passed'] for r in controls),'controls':controls}
        (ROOT/'exact_results.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2));return 0 if result['all_controls_passed'] else 1
    (ROOT/'cycle_results.json').unlink(missing_ok=True)
    assert LEAN.is_file() and LAKE.is_file() and (MATHLIB/'lakefile.lean').is_file()
    version=subprocess.check_output([str(LEAN),'--version'],cwd=MATHLIB,text=True).strip()
    assert 'version 4.33.1,' in version
    revision=subprocess.check_output(['git','-C',str(MATHLIB),'rev-parse','HEAD'],text=True).strip();assert revision==REVISION
    sources={name:(ROOT/name).read_text() for name in FILES}
    base_env=os.environ.copy();base_env['PATH']=str(LEAN.parent)+os.pathsep+base_env.get('PATH','')
    env=json.loads(subprocess.check_output([str(LAKE),'env','python','-c',
        'import json,os; print(json.dumps(dict(os.environ)))'],cwd=MATHLIB,env=base_env,text=True))
    CACHE.mkdir(parents=True,exist_ok=True);LOGS.mkdir(exist_ok=True)
    builds=[];bridge=sources['GateProposalBridge.lean'];suffix='\nopen Researcher040282\n'
    cases=[('positive',bridge,'positive'),
      ('false_previous_row_bound',bridge+suffix+'''\nexample : max 0 ((1-(1/2:ℚ))*3+(1/2)*0) ≤ (1-(1/2:ℚ))*1+(1/2)*0 := by
  norm_num
''','false_math'),
      ('false_without_h_lower',bridge+suffix+'''\nexample : max 0 ((1-(-1:ℚ))*1+(-1)*(-2)) ≤ (1-(-1:ℚ))*1+(-1)*0 := by
  norm_num
''','false_math'),
      ('false_without_h_upper',bridge+suffix+'''\nexample : max 0 ((1-(2:ℚ))*0+2*0) ≤ (1-(2:ℚ))*1+2*0 := by
  norm_num
''','false_math'),
      ('false_zero_row_ratio',bridge+suffix+'''\nexample : appliedNodeScale (fun _ : Fin 12 => (1:ℝ)) 1 (fun _ _ => 0) 0 ≤ (1:ℝ)/0 := by
  norm_num [appliedNodeScale, feasible, rowSum]
''','false_math'),
      ('false_candidate_equals_applied',bridge+suffix+'''\nexample : appliedNodeScale (fun _ : Fin 12 => (1:ℝ)) 2 (fun _ _ => 0) 0 =
    nodeScale (fun _ : Fin 12 => (1:ℝ)) 2 (fun _ _ => 0) 0 := by
  norm_num [appliedNodeScale, nodeScale, feasible, rowSum]
''','false_math'),
      ('sorry_payload',bridge+'''\ntheorem falseWithBridgeHole : (0:ℚ) = 1 := by sorry
#print axioms falseWithBridgeHole
''','sorry_payload'),
      ('extra_axiom_payload',bridge+'''\naxiom injectedBridgeEquality : (0:ℚ) = 1
theorem falseWithBridgeAxiom : (0:ℚ) = 1 := injectedBridgeEquality
#print axioms falseWithBridgeAxiom
''','extra_axiom_payload'),
      ('missing_footprint',bridge.replace('#print axioms Researcher040282.weightStep_factor_lower_of_drive_bounds\n',''),'missing_footprint')]
    print('Fresh dependency builds, then fresh bridge/control sources.',flush=True)
    with tempfile.TemporaryDirectory(prefix='r040282-c003-dependencies-',dir=CACHE) as tmp:
        dependencies=Path(tmp);dep_env=env.copy();dep_env['LEAN_PATH']=str(dependencies)+os.pathsep+env.get('LEAN_PATH','')
        for filename in FILES[:2]:
            name=Path(filename).stem;run,elapsed=compile_one(name,sources[filename],dependencies,dep_env)
            checked=assess(sources[filename],run.returncode,run.stdout)
            builds.append({'module':name,'raw_lean_exit':run.returncode,'seconds':elapsed,**checked})
            assert checked['verified'], 'Dependency proof build failed: '+name
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            controls=list(pool.map(lambda case:compile_case(case,dependencies,env),cases))
    (LOGS/'Candidate.log').unlink(missing_ok=True)
    controls+=exact_controls()+[optimization_control()]
    result={'agent':'Researcher 040282','cycle':3,'compiler_version':version,'mathlib_revision':revision,
        'source_files':{name:hashlib.sha256(text.encode()).hexdigest() for name,text in sources.items()},
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'dependency_builds':builds,'controls':controls,'control_count':len(controls),
        'all_controls_passed':all(r['control_passed'] for r in controls),
        'elapsed_seconds':time.perf_counter()-started,
        'scope':'local closed-file proof/exact harness; no independent-seat approval, engine linkage, or integration'}
    (ROOT/'cycle_results.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in controls:print(r['case'],'PASS' if r['control_passed'] else 'GAP',
        'raw_lean_exit='+str(r.get('raw_lean_exit','not applicable')),
        'verified='+str(r.get('verified','not applicable')),flush=True)
    print('All controls passed:',result['all_controls_passed'],flush=True)
    return 0 if result['all_controls_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
```

## Appendix E — Complete optional controlled-source checker

<!-- FILE: compare_source.py -->
```python
"""Preregistered finite controlled-R check of actual adaptive engine B updates.

The actual compute_R is deliberately replaced for a single call, then restored.
This is NOT a coupled coherence/EMA/delay/phase trajectory or a float64 theorem.
"""
from __future__ import annotations
import sys
if not __debug__:
    raise SystemExit('Run with Python assertions enabled, without -O/-OO.')
from fractions import Fraction as F
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import random
import time
import numpy as np

ROOT=Path(__file__).resolve().parent
SOURCE=Path(os.environ.get('R040282_AIEFS_ENGINE',ROOT/'source_state/main/aief_experiment_engine_v1.py')).expanduser().resolve()
ABS_TOL=5e-15
GAP_MARGIN=1e-8
SEED=2026110703

def zeros(n):return [[F(0) for _ in range(n)] for _ in range(n)]
def fraction(x):return F.from_float(float(x))

def oracle(b,r,cfg):
    n=len(b);b=[[fraction(x) for x in row] for row in b];r=[[fraction(x) for x in row] for row in r]
    dt,eta,mu,gamma,a,q,delta,eps,cap=[fraction(getattr(cfg,name)) for name in
        ['dt','eta','mu','gamma','a','q','delta','scale_epsilon','capacity']]
    p=[[F(0) if i==j else max(F(0),b[i][j]+dt*((eta+mu)*r[i][j]-mu-gamma*b[i][j]))
        for j in range(n)] for i in range(n)]
    rows=[sum(row,F(0)) for row in p]
    gap=min(a-q*row for row in rows)
    active=any(row>cap for row in rows)
    assert active==(gap<delta)
    distance=abs(gap-delta)
    assert distance>fraction(GAP_MARGIN), 'Preregistered guard separation failed; do not discard this case'
    scale=[min(F(1),cap/(row+eps)) for row in rows] if active else [F(1)]*n
    out=[[p[i][j]*min(scale[i],scale[j]) for j in range(n)] for i in range(n)]
    return np.array([[float(x) for x in row] for row in out]),active,float(distance)


def main():
    (ROOT/'source_comparison_results.json').unlink(missing_ok=True)
    started=time.perf_counter();assert SOURCE.is_file()
    spec=importlib.util.spec_from_file_location('r040282_cycle003_engine',SOURCE)
    engine=importlib.util.module_from_spec(spec);sys.modules[spec.name]=engine;spec.loader.exec_module(engine)
    cfg=engine.ModelConfig(
        N=engine.FROZEN_N, dt=engine.FROZEN_DT, tau=engine.FROZEN_TAU,
        omega=tuple(float(x) for x in engine.FROZEN_OMEGA), a=engine.FROZEN_A,
        q=engine.FROZEN_Q, delta=engine.FROZEN_DELTA, eta=engine.FROZEN_ETA,
        mu=engine.FROZEN_MU, gamma=engine.FROZEN_GAMMA, T_window=engine.FROZEN_T_WINDOW,
        B_c=engine.FROZEN_B_C, B_init_scale=engine.FROZEN_B_INIT_SCALE)
    cfg.validate();n=cfg.N;assert n==12 and cfg.gamma>0
    cap=fraction(cfg.capacity);cases=[]
    for k in [3,4,6,12]:
        b=zeros(n);r=zeros(n)
        for i in range(k):
            for j in range(i):b[i][j]=b[j][i]=cap/(k-1);r[i][j]=r[j][i]=F(1)
        cases.append(('active_clique_'+str(k),b,r,True))
    for level in [F(0),F(3,7),F(1,2),F(1)]:
        b=zeros(n);r=zeros(n)
        for i in range(n):
            for j in range(i):b[i][j]=b[j][i]=cap/(4*11);r[i][j]=r[j][i]=level
        cases.append(('inactive_dense_R_'+str(level),b,r,False))
    rng=random.Random(SEED)
    for index in range(16):
        b=zeros(n);r=zeros(n)
        for i in range(n):
            for j in range(i):
                b[i][j]=b[j][i]=cap/(2*11)*F(rng.randint(0,16),16)
                r[i][j]=r[j][i]=F(rng.randint(0,16),16)
        cases.append(('inactive_random_'+str(index),b,r,False))
    assert len(cases)==24
    recorded=[]
    for index,(label,b,r,expected_active) in enumerate(cases):
        b=np.array([[float(x) for x in row] for row in b]);r=np.array([[float(x) for x in row] for row in r])
        expected,active,distance=oracle(b,r,cfg);assert active==expected_active
        state=engine.initialize_state(index,cfg);state.B[:]=b
        original=engine.compute_R
        engine.compute_R=lambda state,config:r.copy()
        try:
            _,_,info=engine.advance_state(state,cfg,np.random.default_rng(index),shuffle_driver=False)
        finally:engine.compute_R=original
        error=float(np.max(np.abs(state.B-expected)))
        assert bool(info['pre_violation'])==active
        assert error<=ABS_TOL,(label,error)
        recorded.append({'case':label,'active':active,'gap_boundary_distance':distance,'max_absolute_error':error})
    assert sum(x['active'] for x in recorded)==4
    result={'agent':'Researcher 040282','cycle':3,'source':str(SOURCE),
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'scope':'finite controlled-R actual-engine weight steps; compute_R overridden only in process; not coupled dynamics or a float64 theorem',
        'python':sys.version.split()[0],'numpy':np.__version__,'pandas':importlib.metadata.version('pandas'),
        'case_count':len(recorded),'active':4,'inactive':20,'all_passed':True,
        'absolute_tolerance':ABS_TOL,'relative_tolerance':0,'guard_separation_required':GAP_MARGIN,
        'maximum_absolute_error':max(x['max_absolute_error'] for x in recorded),
        'random_case_seed':SEED,'seconds':time.perf_counter()-started,'cases':recorded}
    (ROOT/'source_comparison_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
```
