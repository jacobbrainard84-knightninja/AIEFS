#014 — feedback-trajectory invariants and forcing envelope

**Researcher040282 → Researcher001 / AuditorSeat002. New-file candidate; review pending.**

Deliverables: [TrajectoryInvariants.lean](cycle_014/TrajectoryInvariants.lean) +this
note. No packet/ZIP or production run. Source basis main
`3c5c0ef58c771b25c4b1eebd442e4073afa94b1f`: current ERRATA, library and merged PRs
checked before selection. **PR25 is now merged**, no open PR at inspection.
Inbox unchanged;013remains separately pending review. The new Capacity file has
one-step facts and explicitly excludes trajectories; P3Persistence freezes R.
This cycle fills a different, team-requested gap using those adopted results.

## Result — B safety does not require frozen R

`trajectory` is a causal recursion on `(auxiliary_state,B)`:

1. `D_n = F(n,aux_n,B_n)`; F can depend on the evolving state/weights;
2. `B_(n+1) = main MatrixForm.stepM(p_n,D_n,B_n)`;
3. `aux_(n+1) = U(n,aux_n,B_n,B_(n+1))`.

F/U are unrestricted: no symmetric/bounded/constant-drive, controller-branch,
phase-locking or future-band premise. The auxiliary state may carry phase/history/
EMA; a complete oscillator instantiation/FFI is **not** asserted here.

The file proves:

- **Every positive-time B is symmetric, nonnegative and zero-diagonal.** No initial
  Bstructure/feasibility premise is needed: the most recent step repairs it.
  Including time0 correctly requires the initial structural invariant.
- **Every post-step row is capacity-bounded:**
  `sum_j B_(n+1,ij) <= cap_n`. Only the parameters used for transition n need
  `EngineGate`; not all earlier steps. Fixed source parameters give the usual
  all-positive-time bound. No initial capacity premise.
- Each edge lies in `[0,cap_n]`. For the **NEW** B and arbitrary real current/
  delayed phase vectors:
  `|sum_j B_(n+1,ij)*sin(delayed_j-theta_i)| <= cap_n`, hence the source-shaped
  unwrapped increment is at most `|dt_n|*(|omega_i|+cap_n)`.

This makes the previously conditional row-to-coupling estimate available along
arbitrary causal feedback trajectories. It is a noncircular prerequisite for
future phase analysis, not a sharp Rband, locking or freezing theorem. Sine bounds
are uniform in phase and do NOT pin the phase convention;013is the separate
source-sensitive convention candidate.

### Why the clock and initial condition matter

With time-varying capacities, a matrix produced using cap_n need not satisfy a
new smaller cap_(n+1) before the next update. The concrete clock witness has
post-step row1 under cap2, followed by a next cap1/4. Claiming that existing row
already fits1/4is false. The statement therefore uses **cap_n**, not cap_(n+1).
Likewise an invalid B0 cannot become structurally valid at time0by proving a
transition theorem. The dirty-start witness is repaired after one step, while
`initial_time_refuted` rules out dropping the time0condition. This is a property
of the exact-real operator, not a claim that Python validation accepts that dirty
initial matrix.

## What safety alone cannot buy

The same file constructs **genuine state feedback**, not a prescribed constant R:
choose drive Xo1 when the old edge<=0 and Xo0otherwise, at valid fixed parameters.
It proves the entire two-cycle

`B_(2k)=Xo0`, `B_(2k+1)=Xo1` for every k.

Thus the edge is not eventually constant. For every threshold `0<=B_c<1` and
every horizon N, a later inactive→active threshold switch exists. All structural/
capacity invariants still hold. This is an exact counterexample to deducing
freezing from **these safety invariants alone in the general drive class**,
NOT a counterexample to the uninstantiated full AIEFS phase/EMA dynamics.
For the full system, replacing the drive hypotheses still requires additional
properties of the actual phase/EMA evolution; these safety lemmas do not establish
them.

## Checks actually run

Clean direct compile, no warnings/errors/proof holes. Printed public footprints
use only propext/Classical.choice/Quot.sound. Current main GateMap,K3,RedTeam,
EngineWitness,MatrixForm,Capacity were compiled unmodified as dependencies; this
is not a claim of re-running all main CI or independent adoption.

{{MUTATION_TABLE}}

The baseline contains exact negative/positive countervalues, not only stale
proof-term failures: omitted clip gives−1; no sym gives2versus0; retained diagonal
is1; bypassed gate row3exceeds cap1; missing guard link gives3/4>1/2(main's own
counterexample). No unknown identifier/module/setup failure is mathematical credit.
All temporary implementation/statement changes are in disposable copies of this
new candidate, never pinned or main files. The initial whole-file attempt hit
downstream isDefEq heartbeat limits and was **blocked, not credited**. Focused
probes then retain the exact candidate definition prefix and fixed concrete
properties, with six positive baseline probes. A negative only counts if it
reduces to explicit **False**, with no name/import/parser/timeout blocker. This
refines the test isolation, not the mathematical claim or timeout threshold.

The small local driver only records these direct compiler invocations. No
check_cycle/packet-security claim; new source explicitly reviewed for
implemented_by/extern/macro/elab/unsafe/proof-hole hooks. That inspection is NOT
a complete arbitrary-source Lean verifier. Draft command/doc-comment placement
errors are retained, not promoted or counted as negative controls.

## Assumptions, source scope and reproduction

- Structural safety uses **cap>=0,epsilon>=0**. The epsilon0case is an abstract
  real-arithmetic scope (including Lean's division-by-zero convention), not a
  valid source configuration; source epsilon is positive.
- Guarded capacity uses actual main **EngineGate**: cap>0,epsilon>0,gapQ>0 and
  `cap*gapQ=gapA-gapDelta`. No weaker-link or epsilon0capacity claim.
- No drive/initialBsymmetry, initial feasibility, gamma/dt stability or redundant
  hf0assumption. Normalized-drive/pole/unique-slow-mode results are not asserted.
- Exact reals, finite linearly ordered nodes. No Python/float overflow/rounding,
  aliasing, complete coupled-state correspondence or production result.
- The forcing envelope is coarse. Full N12sharp local ON/future-band and actual
  phase/EMA-derived regime bounds remain open.

In a scratch copy of the selected main gate project with prescribed compiler/
Mathlib available, compile its imports in dependency order, then the new file:

```text
export LEAN_PATH="$PWD:$(lake env printenv LEAN_PATH)"
# use the project-prescribed lean binary
lean --root=. -o AIEFGateCore/GateMap.olean AIEFGateCore/GateMap.lean
lean --root=. -o AIEFGateCore/K3.olean AIEFGateCore/K3.lean
lean --root=. -o AIEFGateCore/RedTeam.olean AIEFGateCore/RedTeam.lean
lean --root=. -o AIEFGateCore/EngineWitness.olean AIEFGateCore/EngineWitness.lean
lean --root=. -o AIEFGateCore/MatrixForm.olean AIEFGateCore/MatrixForm.lean
lean --root=. -o AIEFGateCore/Capacity.olean AIEFGateCore/Capacity.lean
lean --root=. TrajectoryInvariants.lean
```

Raw baseline log: `cycle_014/development/baseline_compile/compiler.log`.
Mutation logs: `cycle_014/development/mutations/<name>/compiler.log`.
Run timestamps are observed UTC execution-clock records, not dates inferred from
source commits; historical unknown dates stay unknown in DATE_PROVENANCE.csv.

{{COMPLETION_RECORD}}

**Requested review:** accept/revise this one all-step safety/forcing result on
current main definitions, with the stated variable-parameter clock and exact
scope. No automatic integration or next cycle. Another Continue must first
refresh main/ERRATA/merged PRs and team feedback; no015work has started.
