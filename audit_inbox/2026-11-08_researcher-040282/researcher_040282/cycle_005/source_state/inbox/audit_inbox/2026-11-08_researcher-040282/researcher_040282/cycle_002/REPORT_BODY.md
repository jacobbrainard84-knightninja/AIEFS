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
