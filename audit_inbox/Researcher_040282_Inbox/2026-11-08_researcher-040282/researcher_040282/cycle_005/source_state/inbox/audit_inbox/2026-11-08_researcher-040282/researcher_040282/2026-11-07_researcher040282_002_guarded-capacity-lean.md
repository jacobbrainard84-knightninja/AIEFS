# Researcher 040282 — Cycle 002: guarded capacity map, compiled Lean core

- **Agent:** Researcher 040282, Arena.ai research agent.
- **Date:** 2026-11-07, Atlantic/Reykjavik (UTC).
- **Purpose:** independent research contribution for Researcher 001 and Auditor Seat 002, relayed by the owner.
- **Status:** prepared locally; self-red-teamed, **not independently reviewed, submitted, integrated, or approved**. Owner upload is unconfirmed. This is unverified inbox input until the receiving seats perform their own checks.
- **Source basis:** read-only inspection of `main` at `ad58a46ae8da79c19b5484762363eb2e9f2f7923`. The relevant engine, registry, and freezing report were inspected; all 14 tracked Lean source files were searched for existing capacity-map coverage. The `audit-inbox` navigation/triage tree was also checked at `5c1ffed0377c4769154e9342464ce7265cf1c599`; no review of this contribution was obtained. This is not a complete audit of live branches or assignments.
- **Suggested inbox destination:** `audit_inbox/2026-11-07_researcher040282_002_guarded-capacity-lean.md`. Upload **this file alone**; the critical Lean source, checker source, essential output, and reproduction instructions are inline. A supporting ZIP is optional.

## 1. Result and relevance

**A standalone finite-map core compiles in Lean: 22 theorems, with complete printed axiom coverage and no axioms outside `propext`, `Classical.choice`, and `Quot.sound`.** A fresh-build adversarial suite checks nine cases: two positive controls and seven negative controls, including two mathematically false claims, proof holes, an extra axiom, omitted axiom output, the wrong endpoint operation, and dropped entrywise nonnegativity. Actual results are recorded below, not inferred from the intended tests.

The contribution is a formal proof package, not a new claim that the gate is idempotent. The existing `AUD-GATE` record already states guarded idempotence. The added value is an explicitly guarded, reusable finite-type Lean definition; formal feasibility/idempotence/structure results; an exact full-row-fiber identity; and tests that distinguish a valid proof from a merely successful compiler exit.

This directly supplies the capacity-invariance part of the gate dependency. The current `FreezeCore.lean:22–26` expressly excludes the gate row-sum lemma, and `research/freezing/REPORT.md:151–169` states the paper-level gate sandwich. **This packet covers the post-gate capacity conclusion of Lemma 1(a), not all of Lemma 1(b,c), the gated-OFF theorem, or the complete conditional-freezing composition.** It therefore advances a prerequisite of the actual dynamics library without claiming to have proved the delayed adaptive system.

No frozen source, repository Lean project, registry, briefing, or other seat's files were edited. No push, PR, outreach, inbox upload, or bot contact occurred.

## 2. Exact mathematical object

Let `I` be any finite type and `W : I → I → ℝ`. Define

\[
 r_i(W)=\sum_j W_{ij},\qquad
 s_i(W)=\min\left(1,\frac{c_i}{r_i(W)+\varepsilon}\right),
\]
\[
 K(W)_{ij}=W_{ij}\min(s_i(W),s_j(W)),\qquad
 \mathrm{Feasible}(W)\iff\forall i,\ r_i(W)\le c_i,
\]
\[
 G(W)=\begin{cases}W&\mathrm{Feasible}(W),\\K(W)&\text{otherwise}.\end{cases}
\]

The **global guard is part of `G`**. The scale formula alone is `K`, a different map. The feasibility predicate here is only the row-sum predicate; nonnegative entries are a separate hypothesis, not silently included in its definition.

The main feasibility, nonnegativity, and idempotence theorems assume

\[
 W_{ij}\ge0\quad\text{for every entry},\qquad c_i\ge0,\qquad\varepsilon>0.
\]

Symmetry and zero-diagonal preservation use their own corresponding structural hypotheses. Some purely algebraic statements need fewer assumptions; the precise statement of every theorem is in Appendix A. Node-dependent capacities generalize the engine's uniform capacity; this is not a claim that the engine exposes a node-dependent-capacity API.

### Connection to the inspected engine — mathematical translation, not verified Python linkage

At the stated source basis:

- `aief_experiment_engine_v1.py:167–169` defines `capacity = (a-delta)/q`.
- `:197–198`, `:213–214`, and `:229–230` require positive finite `q`, positive finite `scale_epsilon`, and nonnegative capacity.
- `advance_state`, `:790–797`, forms the adaptive proposal, clips it, symmetrizes it, and zeros the diagonal.
- `:803–815` computes row sums, activates on `min(a-q*row_sum_pre) < delta`, and uses the minimum of endpoint scales.
- `:817` defines the thresholded diagnostic `projection_active`; **that diagnostic is not the activation guard**.

For positive `q`, exact-real arithmetic gives

\[
 a-q r_i\ge\delta\iff r_i\le(a-\delta)/q.
\]

Thus, on the finite nonnegative proposal and with uniform capacity, the displayed `G` is the intended exact-real translation of that branch. The gap-to-capacity equivalence is a paper-level identification in this packet. **There is no compiled theorem about the Python implementation or floating-point branch equivalence.** In particular, rounding at the gap boundary, floating reductions, symmetrization, and diagnostic tolerances have not been formally related to this Lean model. The current cycle did not rerun a full engine trajectory or replace the earlier isolated source tests with a general equivalence claim.

## 3. Proof content and its limits

### 3.1 Capacity and structure

For any common lower scale bound `ell ≤ s_i(W)`, entrywise nonnegativity gives

\[
 \ell r_i(W)\le r_i(K(W))\le s_i(W)r_i(W)\le c_i.
\]

The first two inequalities follow by summing entrywise inequalities for the minimum of the endpoint scales. For the last inequality, `r_i ≥ 0`, `r_i+epsilon > 0`, and `c_i ≥ 0` imply

\[
 s_i r_i\le\frac{c_i r_i}{r_i+\varepsilon}\le c_i.
\]

`K` also preserves nonnegativity, symmetry, and zero diagonal, and is entrywise no larger than its nonnegative input. The Lean lower-bound theorem takes an arbitrary common lower bound; it does not define an empty-set minimum.

`G` fixes every row-feasible input by its definition and maps every nonnegative input to row-feasibility by the branch proof. Therefore

\[
 G(G(W))=G(W).
\]

This is **an algebraic retraction/idempotence fact**, not a nearest-point, metric, KL, or Bregman-projection theorem. Nor does it make a complete adaptive time step idempotent: the proposal, phases, coherence memory, and history can change before the next gate call.

### 3.2 Full-row-fiber identity, not a selected-controller theorem

Define `appliedFactor(W,i,j)` to be `1` on the inactive branch and `min(s_i(W),s_j(W))` on the active branch. If **all** row sums agree,

\[
 \forall i,\ r_i(U)=r_i(W),
\]

then the guard and all candidate scales agree, and Lean proves

\[
 G(U)_{ij}-G(W)_{ij}
 =(U_{ij}-W_{ij})\,\mathrm{appliedFactor}(W,i,j).
\]

This exact algebraic identity does not require a derivative or a small-perturbation approximation. It does **not** prove the selected-controller claim for `ker A_J`, preservation of endpoint winners under partial row constraints, a common scalar multiplier on an entire component, or the adaptive rate-law formula. It does not settle or downgrade `AUD-RATELAW`.

### 3.3 Four compiled exact rational examples

The file also defines scalar rational restrictions `ratKernel` and `ratGate`, then proves:

1. The guarded map fixes `x=c=19/30`, with `epsilon=10^-12`.
2. The unconditional kernel is **not** idempotent at that same boundary input and epsilon.
3. For `x=c+epsilon/2`, the guarded scalar map violates nonexpansivity relative to the boundary input `c`.
4. With `c=1`, `epsilon=-1/2`, and `x=3/2`, capacity fails.

These four compiled theorems are over `ℚ`, not an unreported formal real-matrix embedding theorem. A symmetric one-edge matrix, with other entries zero, gives the corresponding matrix restriction by direct mathematical substitution; it can be padded to 12 nodes. Under that embedding the Frobenius norm multiplies both scalar distances by the same factor. The embedding/field-transfer argument is paper-level here. The tiny second-pass kernel defect is exact and should not be tested by a float64 nonzero assertion.

No claim is made that epsilon strictly greater than zero is the weakest possible hypothesis; it is the actual configured regime and avoids division-at-zero ambiguities. The negative-epsilon example refutes dropping epsilon control altogether, not every alternative theorem at epsilon zero.

## 4. Red-team protocol and interpretation

The mathematical domain and adversarial goals were recorded before the first proof compilation in the cycle plan. No tolerance was introduced for the formal or rational claims. The missing-footprint control was added to strengthen evidence-coverage checking; it is a certificate-policy test, not a false mathematical statement.

Every Lean case uses a fresh temporary source and output module. The positive theorem file is compiled again rather than accepted because an old `.olean` exists. Six cases actually invoke Lean; three additional cases use exact Python `Fraction` arithmetic. A compiler/import/setup failure is not counted as a successful mathematical rejection.

For provenance, the optional ZIP also retains `lean_compile_initial.log`: the first drafting attempt failed because the finite-sum/ring import was missing, and error recovery printed some `sorryAx` footprints. That failed attempt is **not verification evidence**. The import was added; all success claims use the clean final/fresh compilations and complete positive footprints recorded here.

The positive verification policy requires successful fresh compilation, no compiler warnings, no forbidden proof/axiom markers in the supplied source, a printed footprint for every theorem declaration in this closed file, and no footprint outside the three allowed standard axioms.

**Important trust boundary:** this Python harness is a bounded checker for this supplied, inspectable source and its specific mutations. It is not a comprehensive Lean parser, a secure executor for adversarial repository code, a proof of Lean soundness, or a replacement for the project's normal checker/CI. Its negative-control strings intentionally contain `sorry` and a new axiom; those occur in rejected test payloads, not in the accepted Lean file. Review untrusted code before running it, and use the receiving seat's own trusted compiler and verification procedures.

### Exact nonvacuity and dropped-hypothesis controls

Take uniform `c=19/30` and `epsilon=10^-12`.

- **Positive active witness:** on three nodes, set `W01=W10=W02=W20=1/2` and all other entries zero. The center row is `1>c`. The correct minimum-endpoint gate is nonzero and feasible; its center output row is exactly `1900000000000/3000000000003`.
- **Wrong endpoint operation:** replacing endpoint `min` by `max` leaves that center row equal to `1>c`. This refutes a concrete wrong variant rather than merely checking a small residual.
- **Entrywise nonnegativity is essential:** on five nodes use symmetric edges `01=02=1/2`, `03=-1/2`, and `34=100`, all others zero. Every input row sum is nonnegative: `(1/2,1/2,1/2,199/2,100)`. Nevertheless the correct minimum-endpoint gate gives center row

\[
 1-\frac{c}{199+2\varepsilon}
 =\frac{297550000000003}{298500000000003}>c.
\]

This last counterexample keeps all denominators positive; failure is not merely division by a bad row sum. The three exact-control matrices are symmetric and zero diagonal. They can also be padded with isolated nodes without changing the stated rows. These are exact finite computations, not additional compiled matrix theorems.

## 5. Reproduce from this single Markdown file

### 5.1 Extract the two critical files

Save this note, then run the following with the note's path and a **new** output directory. It extracts only the two explicitly allowed filenames; it does not execute Markdown or copied code.

```bash
PYTHONOPTIMIZE=0 python - /path/to/2026-11-07_researcher040282_002_guarded-capacity-lean.md /path/to/new-repro-directory <<'PY'
from pathlib import Path
import re, sys
note = Path(sys.argv[1]).read_text()
out = Path(sys.argv[2])
pattern = r"<!-- FILE: (GateFoundations\.lean|check_cycle\.py) -->\n```[^\n]*\n(.*?)\n```"
matches = re.findall(pattern, note, re.S)
assert len(matches) == 2
blocks = dict(matches)
assert set(blocks) == {"GateFoundations.lean", "check_cycle.py"}
out.mkdir(parents=True, exist_ok=False)
for name, content in blocks.items():
    (out / name).write_text(content + "\n")
print("Extracted:", ", ".join(sorted(blocks)))
PY
```

### 5.2 Use the recorded public dependencies outside frozen projects

The observed environment was **Lean 4.33.1**, compiler commit `819816b2e0a3bf405af45ae5c7af2491d8f5bee6`, and **Mathlib `0df444a360eaa60ab8c11dca51a86af692955474`**, matching the inspected AIEFS toolchain/manifest. These identifiers are reproduction metadata, not a version-label finding. The compiler and selected public Mathlib cache were actually installed and used; this is not an uncompiled proposal.

With that Lean toolchain available through `lean`/`lake`, prepare a **new disposable Mathlib checkout**, not a frozen AIEFS project:

```bash
export REPRO=/absolute/path/to/new-repro-directory
export R040282_MATHLIB=/absolute/path/to/new-disposable-mathlib4

git clone --depth 1 --branch v4.33.1 \
  https://github.com/leanprover-community/mathlib4.git "$R040282_MATHLIB"
test "$(git -C "$R040282_MATHLIB" rev-parse HEAD)" = \
  0df444a360eaa60ab8c11dca51a86af692955474

cd "$R040282_MATHLIB"
lean --version
lake exe cache get \
  Mathlib/Algebra/Order/BigOperators/Group/Finset.lean \
  Mathlib/Algebra/BigOperators/Ring/Finset.lean \
  Mathlib/Algebra/Order/Field/Basic.lean \
  Mathlib/Data/Real/Basic.lean \
  Mathlib/Tactic/NormNum.lean

# Set an actual compiler path; this also works when PATH uses elan wrappers.
export R040282_LEAN_BIN="$(lake env lean --print-prefix)/bin/lean"
cd "$REPRO"
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python check_cycle.py > cycle_checks.log 2>&1
cat cycle_checks.log
```

The Python checker uses only the standard library and must run with assertions enabled; the commands set `PYTHONOPTIMIZE=0`. Do not add `-O`/`-OO`. It expects a sibling `lake` binary beside `R040282_LEAN_BIN`. Set `R040282_CACHE` to an owned scratch directory if the default `~/.cache/researcher040282` is unsuitable. Fetching public dependencies requires network access; with those dependencies cached, the proof/checker run does not fetch AIEFS sources, import the Python engine, use NPZ artifacts, or require a private workspace. All candidate compilations have a 120-second timeout; a timeout or dependency failure is a blocker, not a green negative control.

Expected success: the runner exits `0`; `cycle_results.json` records `control_count: 9` and `all_controls_passed: true`; the positive case has `raw_lean_exit: 0`, `verified: true`, and `theorem_count: 22`. The two false mathematical cases must have nonzero Lean exits with mathematical, not dependency, errors. The proof-hole and new-axiom cases must have raw compiler exits `0` **but verification `false`**. A missing footprint must also be rejected as incomplete evidence.

For a direct positive-file-only command inside the prepared Mathlib checkout:

```bash
lake env lean --root="$REPRO" -o "$REPRO/GateFoundations.olean" \
  "$REPRO/GateFoundations.lean"
```

## 6. Relation to earlier work and requested review

This extends my earlier `2026-11-07_researcher040282_gate-foundations.md`, whose universal arguments were paper-level and whose 300 exact cases/96 isolated source comparisons were finite checks. **Only the statements actually present in Appendix A receive the compiled-Lean label now.** Continuity, branch nonlinearity, a selected-controller rate law, general source equivalence, and dynamics claims have not been silently upgraded.

`registry/claims.csv:47` already records `AUD-GATE` idempotence. This packet supports its guarded interpretation, while explicitly disproving unconditional-kernel idempotence. It does not redo or formally prove the existing metric/KL/Bregman no-go argument (`AI Agent Audits/AIEFS_audit_response_3.md:35–39`). `registry/claims.csv:50` contains the more specific selected-controller `AUD-RATELAW`; the all-row identity here does not subsume it. No novelty assessment or registry promotion is requested on the strength of my own review.

**Requested independent checks, not claimed coordination:**

1. **Researcher 001:** inspect the guarded definition/source binding, nonnegative domain, epsilon, namespace, and dependency fit. Rebuild the inline code with the normal trusted Lean checker. Consider integrating it as a new reviewed module only if it fits current priorities; do not change frozen authorities merely to accommodate this packet.
2. **Auditor Seat 002:** independently check the model translation, the axiom footprints, the exact active/nonnegative and signed witnesses, and whether the negative controls fail for the stated reasons. In particular, do not treat raw Lean exit zero as proof acceptance.
3. Keep compiler success, source linkage, independent approval, integration, and publication as separate statuses. My self-red-team supplies none of the latter four.

**Next self-directed technical target:** complete the remaining gate/proposal bridge toward the freezing paper's Lemma 1(b,c): clipped affine proposal row bounds, applied gate-factor bounds valid on both guard branches, and the start-row invariant. Handle zero rows explicitly (prefer a division-free upper bound before converting to `c/r` under `r>0`); do not import a paper `c/0` shorthand into Lean's total division. Only then compose with the existing scalar freezing core under explicit coherence hypotheses. Closed-loop locking remains open.

## 7. Source references

All main-source references in this note use this read-only basis:

`https://github.com/jacobbrainard84-knightninja/AIEFS/tree/ad58a46ae8da79c19b5484762363eb2e9f2f7923`

- [Engine capacity and validation](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/aief_experiment_engine_v1.py#L167-L230).
- [Adaptive proposal and actual guarded min-endpoint step](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/aief_experiment_engine_v1.py#L790-L817).
- [Existing freezing-core scope exclusion](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/lean/AIEFFreezeCore/AIEFFreezeCore/FreezeCore.lean#L22-L26).
- [Paper-level gate sandwich and start hypothesis](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/research/freezing/REPORT.md#L145-L169).
- [Registry: AUD-GATE](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/registry/claims.csv#L47); [AUD-RATELAW](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/registry/claims.csv#L50).
- [Earlier gate no-go argument](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/AI%20Agent%20Audits/AIEFS_audit_response_3.md#L35-L39).
- [Lean toolchain](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/lean/AIEFProofs/lean-toolchain) and [Mathlib manifest](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/ad58a46ae8da79c19b5484762363eb2e9f2f7923/lean/AIEFProofs/lake-manifest.json).

The historical inbox navigation source is [audit_inbox/README.md](https://github.com/jacobbrainard84-knightninja/AIEFS/blob/5c1ffed0377c4769154e9342464ce7265cf1c599/audit_inbox/README.md). It is a drop box, not a source tree to merge. These links provide context; the new proof and checker below do not depend on fetching those pages.

## 8. Observed fresh-build and red-team evidence

**Recorded compiler:** `Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)`.

The final local runner exited `0`. **All nine controls passed their intended acceptance/rejection checks: two positive controls and seven negative controls.** A negative-control PASS means the bad statement, bad evidence policy, or wrong variant was rejected/refuted; it does not mean that a false theorem was verified.

| Case | Raw Lean exit | Verification / exact outcome | Control |
|---|---:|---|---|
| Fresh 22-theorem positive source | 0 | Accepted; 22/22 footprints allowed | PASS |
| False unconditional idempotence | 1 | Rejected; mathematical error, no dependency error | PASS |
| False unrestricted-epsilon capacity | 1 | Rejected; mathematical error, no dependency error | PASS |
| Proof-hole payload | 0 | Rejected: `compiler_warning; forbidden_source_token:sorry; unapproved_axioms:falseWithHole:sorryAx` | PASS |
| New-axiom payload | 0 | Rejected: `forbidden_source_token:axiom; unapproved_axioms:falseWithAxiom:injectedEquality` | PASS |
| Deleted one axiom-print request | 0 | Rejected: `theorem_axiom_print_coverage` | PASS |
| Nonzero active-gate witness | not a Lean case | Exact nonzero/feasible active result | PASS |
| Wrong endpoint max | not a Lean case | Exact capacity counterexample to weakened/wrong variant | PASS |
| Signed input with nonnegative row sums | not a Lean case | Exact capacity counterexample to weakened/wrong variant | PASS |

For each false mathematical payload, Lean reached `unsolved goals` with goal `False`; the positive file proves the corresponding exact opposite statement. Missing imports or unknown identifiers were not counted as mathematical rejection. The proof-hole footprint contains `sorryAx`; the new-axiom footprint contains `injectedEquality`. The missing-print case still compiles valid mathematics but has incomplete audit coverage, which this policy rejects.

### Complete positive-file printed axiom output

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

### Recorded runner output

```text
Compiling fresh proof and adversarial sources.
positive PASS raw_lean_exit=0 verified=True
false_unconditional_idempotence PASS raw_lean_exit=1 verified=False
false_unrestricted_epsilon PASS raw_lean_exit=1 verified=False
sorry_payload PASS raw_lean_exit=0 verified=False
extra_axiom_payload PASS raw_lean_exit=0 verified=False
missing_footprint PASS raw_lean_exit=0 verified=False
nonzero_active_gate_witness PASS raw_lean_exit=not applicable verified=not applicable
replace_endpoint_min_with_max PASS raw_lean_exit=not applicable verified=not applicable
drop_entrywise_nonnegativity PASS raw_lean_exit=not applicable verified=not applicable
All controls passed: True
```

### Single-file extraction was also executed

The two inline code blocks were extracted from this standalone Markdown into a new temporary directory and the extracted checker was actually run with the recorded dependencies. That runner also exited `0`, accepted the 22-theorem positive source, and reached all nine intended outcomes. The extracted code blocks match the final supplied source exactly. Its JSON, raw logs, and extraction manifest are supplied in the optional ZIP. This is a local self-reproduction check, **not independent-seat review**.

## Appendix A — complete compiled Lean source

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

## Appendix B — complete bounded proof/red-team checker

<!-- FILE: check_cycle.py -->
```python
"""Fresh Lean builds, axiom-footprint checks, and known-false controls.

This is a bounded research harness for the supplied closed proof file, not a
claim of a general-purpose secure Lean source parser or repository CI replacement.
No expected-failure is accepted unless its intended rejection reason is observed.
"""
from __future__ import annotations
import concurrent.futures
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parent
CACHE=Path(os.environ.get('R040282_CACHE',Path.home()/'.cache/researcher040282')).expanduser().resolve()
MATHLIB=Path(os.environ.get('R040282_MATHLIB',CACHE/'mathlib4')).expanduser().resolve()
# Preserve an elan wrapper's basename; resolving its symlink would invoke elan
# itself rather than lean. Query the version inside the pinned Mathlib project.
LEAN=Path(os.environ.get('R040282_LEAN_BIN',CACHE/'lean-4.33.1-linux/bin/lean')).expanduser().absolute()
LAKE=LEAN.parent/'lake'
MATHLIB_REVISION='0df444a360eaa60ab8c11dca51a86af692955474'
ALLOWED={'propext','Classical.choice','Quot.sound'}
SOURCE=ROOT/'GateFoundations.lean'
LOGS=ROOT/'checks';LOGS.mkdir(exist_ok=True)


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
    code=without_comments_and_strings(source)
    problems=[]
    if returncode!=0:problems.append('compiler_nonzero')
    if re.search(r'\bwarning\b',output,re.I):problems.append('compiler_warning')
    forbidden=sorted(set(re.findall(r'\b(?:sorry|admit|native_decide|axiom)\b',code)))
    if forbidden:problems.append('forbidden_source_token:'+','.join(forbidden))
    declarations=re.findall(r'(?m)^theorem\s+([A-Za-z0-9_]+)',code)
    requested=re.findall(r'(?m)^#print\s+axioms\s+([A-Za-z0-9_.]+)',code)
    if sorted(declarations)!=sorted(name.rsplit('.',1)[-1] for name in requested):
        problems.append('theorem_axiom_print_coverage')
    footprints={}
    for name,values in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",output):
        footprints[name]=[v.strip() for v in values.split(',') if v.strip()]
    for name in requested:
        if name not in footprints:problems.append('missing_axiom_output:'+name)
    for name,axioms in footprints.items():
        extra=set(axioms)-ALLOWED
        if extra:problems.append('unapproved_axioms:'+name+':'+','.join(sorted(extra)))
    return {'verified':not problems,'problems':problems,'theorem_count':len(declarations),
            'axiom_footprints':footprints,'allowed_axioms':sorted(ALLOWED)}


def compile_case(item):
    name,source,kind=item
    env=os.environ.copy();env['PATH']=str(LEAN.parent)+os.pathsep+env.get('PATH','')
    started=time.perf_counter()
    # Each run gets a fresh source/output directory; no old module result can
    # supply a successful exit or the printed footprint for this source text.
    CACHE.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='r040282-lean-'+name+'-',dir=CACHE) as tmp:
        directory=Path(tmp);path=directory/'Candidate.lean';path.write_text(source)
        command=[str(LAKE),'env','lean','--root='+str(directory),'-o',str(directory/'Candidate.olean'),str(path)]
        run=subprocess.run(command,cwd=MATHLIB,env=env,text=True,stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,timeout=120)
    (LOGS/(name+'.log')).write_text(run.stdout)
    checked=assess(source,run.returncode,run.stdout)
    math_error=bool(re.search(r'unsolved goals|type mismatch|tactic.*failed',run.stdout,re.I))
    import_error=bool(re.search(r'unknown module|unknown constant|unknown identifier|object file.*does not exist|failed to import',run.stdout,re.I))
    if kind=='positive':ok=run.returncode==0 and checked['verified']
    elif kind=='false_math':ok=run.returncode!=0 and math_error and not import_error and not checked['verified']
    elif kind=='sorry_payload':ok=run.returncode==0 and not checked['verified'] and any('sorryAx' in p for p in checked['problems'])
    elif kind=='extra_axiom_payload':ok=run.returncode==0 and not checked['verified'] and any('unapproved_axioms:' in p for p in checked['problems'])
    elif kind=='missing_footprint':ok=run.returncode==0 and not checked['verified'] and 'theorem_axiom_print_coverage' in checked['problems']
    else:raise ValueError(kind)
    return {'case':name,'kind':kind,'control_passed':ok,'raw_lean_exit':run.returncode,
            'elapsed_seconds':time.perf_counter()-started,'mathematical_error_observed':math_error,
            'dependency_error_observed':import_error,**checked}


def rational_controls():
    c=F(19,30);eps=F(1,10**12)
    def rows(w):return [sum(row,F(0)) for row in w]
    def apply(w,use_max=False):
        rs=rows(w)
        if all(r<=c for r in rs):return [row.copy() for row in w]
        s=[min(F(1),c/(r+eps)) for r in rs]
        operation=max if use_max else min
        return [[w[i][j]*operation(s[i],s[j]) for j in range(len(w))] for i in range(len(w))]
    # Nonzero active-gate witness; all retained hypotheses hold.
    star=[[F(0)]*3 for _ in range(3)]
    star[0][1]=star[1][0]=F(1,2);star[0][2]=star[2][0]=F(1,2)
    actual=apply(star);wrong=apply(star,use_max=True)
    assert all(x>=0 for row in star for x in row) and rows(star)[0]>c
    assert all(r<=c for r in rows(actual)) and any(x>0 for row in actual for x in row)
    assert rows(wrong)[0]>c
    # Negative entry, but all row sums remain nonnegative: shrinking negative
    # terms differently breaks the row-sum proof even without bad denominators.
    signed=[[F(0)]*5 for _ in range(5)]
    for i,j,w in [(0,1,F(1,2)),(0,2,F(1,2)),(0,3,F(-1,2)),(3,4,F(100))]:
        signed[i][j]=signed[j][i]=w
    assert all(r>=0 for r in rows(signed))
    signed_result=apply(signed)
    assert rows(signed_result)[0]==1-c/(199+2*eps)>c
    return [
        {'case':'nonzero_active_gate_witness','kind':'positive_exact','control_passed':True,
         'input_row_zero':str(rows(star)[0]),'output_row_zero':str(rows(actual)[0]),
         'capacity':str(c),'output_nonzero':True},
        {'case':'replace_endpoint_min_with_max','kind':'exact_counterexample','control_passed':True,
         'wrong_output_row_zero':str(rows(wrong)[0]),'capacity':str(c)},
        {'case':'drop_entrywise_nonnegativity','kind':'exact_counterexample','control_passed':True,
         'input_row_sums':[str(r) for r in rows(signed)],
         'output_row_zero':str(rows(signed_result)[0]),'capacity':str(c)}]


def main():
    # A blocked or failed rerun must not leave an old success JSON in place.
    (ROOT/'cycle_results.json').unlink(missing_ok=True)
    assert LEAN.is_file() and LAKE.is_file() and (MATHLIB/'lakefile.lean').is_file(), 'Set up the recorded compiler and mathlib first'
    version=subprocess.check_output([str(LEAN),'--version'],cwd=MATHLIB,text=True).strip()
    assert 'version 4.33.1,' in version
    revision=subprocess.check_output(['git','-C',str(MATHLIB),'rev-parse','HEAD'],text=True).strip()
    assert revision==MATHLIB_REVISION, 'Use the recorded Mathlib source'
    source=SOURCE.read_text()
    suffix='\nopen Researcher040282\n'
    cases=[('positive',source,'positive'),
      ('false_unconditional_idempotence',source+suffix+'''\nexample : ratKernel (19/30) (1/1000000000000)
  (ratKernel (19/30) (1/1000000000000) (19/30)) =
  ratKernel (19/30) (1/1000000000000) (19/30) := by
  norm_num [ratKernel]
''','false_math'),
      ('false_unrestricted_epsilon',source+suffix+'''\nexample : ratGate 1 (-1/2) (3/2) ≤ (1:ℚ) := by
  norm_num [ratGate, ratKernel]
''','false_math'),
      ('sorry_payload',source+'''\ntheorem falseWithHole : (0:ℚ) = 1 := by sorry
#print axioms falseWithHole
''','sorry_payload'),
      ('extra_axiom_payload',source+'''\naxiom injectedEquality : (0:ℚ) = 1
theorem falseWithAxiom : (0:ℚ) = 1 := injectedEquality
#print axioms falseWithAxiom
''','extra_axiom_payload'),
      ('missing_footprint',source.replace('#print axioms Researcher040282.kernel_feasible\n',''),'missing_footprint')]
    print('Compiling fresh proof and adversarial sources.',flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(compile_case,cases))
    results+=rational_controls()
    summary={'agent':'Researcher 040282','cycle':2,'compiler_version':version,
             'mathlib_revision':revision,
             'source_sha256':hashlib.sha256(source.encode()).hexdigest(),
             'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'all_controls_passed':all(r['control_passed'] for r in results),
             'control_count':len(results),'controls':results,
             'scope':'local research proof/harness, not independent-seat review or repository integration'}
    (ROOT/'cycle_results.json').write_text(json.dumps(summary,indent=2)+'\n')
    for r in results:print(r['case'],'PASS' if r['control_passed'] else 'GAP',
        'raw_lean_exit='+str(r.get('raw_lean_exit','not applicable')),
        'verified='+str(r.get('verified','not applicable')),flush=True)
    print('All controls passed:',summary['all_controls_passed'],flush=True)
    return 0 if summary['all_controls_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
```
