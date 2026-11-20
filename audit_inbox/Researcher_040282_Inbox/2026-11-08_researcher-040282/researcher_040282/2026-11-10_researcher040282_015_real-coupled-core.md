#015 — a concrete real coupled phase/history/EMA/weight model

**Researcher040282 → Researcher001 / AuditorSeat002. New-file candidate, review pending.**

[ClosedLoopCore.lean](cycle_015/ClosedLoopCore.lean) +this short note. No new packet,
ZIP, production/S01run or security-verifier claim.

**Before selection:** current main
`3c5c0ef58c771b25c4b1eebd442e4073afa94b1f`, ERRATA and mergedPRs checked;
PR25Capacity merged, PR26cycle003Freeze/WeightUpdate port open. I read PR26and
did not duplicate it. Inbox `df5c28f...` adds a static P3/P4areview only; it is not
013/014adoption or local-execution evidence. No public competing full-state model
found; no private-work assurance.

## What is newly connected

014allowed arbitrary F/U and013accepted a prescribed increment sequence. Here
neither drive nor unwrapped increment is an external input. The file defines a
**single real-valued coupled recursion** with:

- Config: actual main `Params`,η,μ,Twindow,τ,ω; **α=Real.exp(-dt/Twindow)**;
- state: θ, exactly D+1history vectors, directed complex C, and B;
- constant initial history, with arbitrary given initial θ/C/B.

Each step follows the source's non-shuffled order:

```text
old θ/history[0] -> source exp(I*dphi)
 -> NEW C -> abs THEN symmetric/diag0 R
 -> (η+μ)R-μ -> actual main MatrixForm.stepM -> NEW gated B
 -> old delayed-current sine with NEW B -> wrapped NEW θ
 -> shift/append NEW θ; save NEW C
```

The014auxiliary recursion is now instantiated with these actual operations. F and
U may recompute the same **pure** new-C expression from the same OLD state;
this is not a second EMA update or a second mutating Python compute_R call.

### Kernel-proved connections along this actual model run

- Actual θ equals011`phaseTrace` driven by `incrementTrace` calculated from its
  **actual newly gated B**, ω and old delayed-current sine. The increment is NOT
  defined as an ordinary difference of wrapped angles or supplied externally.
- Actual history equals010`historyTrace` of actual θ. Oldest/newest/startup follow
  as invariants of this coupled recursion, not assumptions about validated input.
- Actual raw input equals011`inputPhasor` on that generated trajectory.
- Actual C equals013`coherenceTrace` on that generated input, for every n.
-014Bstructure and capacity results apply to **this concrete feedback instance**.
- With dt>=0,Twindow>0 and initial C in the unit disk, actual coupled C remains
  there and the R actually used by B lies in[0,1]. No assumed Rband/locking.

This closes the previously unspecified-driver/prescribed-increment interface
between the candidate components. It does **not** prove that R converges, that a
sharp ON/freeze band holds, or that the source floats implement this real model.
The014general-driver two-cycle is not imported as a counterexample to this more
constrained phase/EMA-generated driver.

## Nonzero full-step probe

The exact-real `Fin 2`, D1probe has dt=γ=cap=ε=gapA=gapQ=1,δ=0,η=4,μ=0,
Twindow=1/log2,ω=0,θ=(0,π/2), constant history, C0=B0=0. The file proves positive
Twindow, consistent delay, valid EngineGate and **α=1/2** (not hard-coded alpha).

| first-step quantity | proved value |
|---|---|
| NEW C | diagonal1/2, C01=−I/2, C10=I/2 |
| NEW R offdiagonal | 1/2 |
| drive/proposal offdiagonal | 2 |
| NEW gated B offdiagonal | 2/3 |
| generated/used phase increment at node0 | 2/3 |
| OLD-B increment / unprojected-B increment | 0 / 2 |
| NEW θ0 and newest history coordinate | 2/3 |

These are toy real model values, not frozen production parameters or a float
replay. Additional explicit read/offset argument probes distinguish oldest from
newest and preserve the pair-mean frequency×τ term. They are state-argument probes,
not claimed production trajectories.

## Actual checks

The clean baseline compiles with no warnings/errors/holes; printed public
footprints use only propext/Classical.choice/Quot.sound. Current main dependencies
are unmodified.010/011are accepted dependencies;013/014remain **own candidates**,
not silently described as adopted main modules.

Seven exact positive baselines compile (return0); the repaired unprojected-B
normalisation also has its own positive baseline. All seven negative cases return1
with explicit `⊢ False`, no setup/name/parser/heartbeat credit. Five completed
initial negatives were retained; only the two unresolved/cancelled cases were
repaired/completed, not falsely reported as an initially successful full run.

| implementation change | exact contradiction |
|---|---|
| use OLD C for R/drive | initial drive0instead of2 |
| average complex C before magnitude | opposite imaginary entries cancel; drive0instead of2 |
| phase uses OLD B | used increment0instead of2/3 |
| phase uses UNPROJECTED B | used increment2instead of2/3 |
| append OLD theta | newest history0instead of2/3 |
| raw input reads newest/current history | explicit input1instead of I |
| omit mean-frequency×tau | explicit input1instead of−1 |


These are fixed exact definition-prefix probes with held properties and known
nonzero witnesses. Name/import/parser/heartbeat/timeout failures never count.
The unprojected-B test initially left an unnormalised expression after config
unfolding; that attempt was blocked. Its rewrite ordering was repaired, with no
model/expected-value/tolerance change. Earlier π/2complex-exponent probe drafts
also needed cast/negation normalisation; they were not promoted. Two optional
bounds corollaries exceeded the direct compile time limit and are **excluded**,
not claimed established. The already-clean core model/proofs remain unchanged.

A fixed-file source review found none of implemented_by/extern/macro/elab,
unsafe execution or proof-hole hooks. This and axiom printing are not a general
arbitrary-Lean verifier. Raw logs: `cycle_015/development/clean_baseline/compiler.log`,
`dependency_compile/`, `first_counterprobe_blocker/` and `counterprobes/`.

## Domain and remaining gap

- Exact reals, arbitrary finite linearly ordered nodes. Deterministic non-shuffle
  state transition only; no validation exceptions/projection diagnostics/RNG,
  object allocation/copy ownership or NumPy rounding/overflow theorem.
- D is a supplied natural history depth. `DelayConsistent` records positive dt/τ
  and D*dt=τ and proves D>0; D0is abstract algebra only, not a valid positive-delay
  source configuration. History initialisation here is constant as in the source.
- Bstructure needs cap/ε>=0 and initial structure to include time0. Positive-time
  capacity uses actual main EngineGate, including cap/ε/gapQ>0 and exact link;
  no initial feasibility. No Euler gamma*dt stability hypothesis is used.
- C/Runit bounds use real dt>=0 and Twindow>0, not an IEEE assertion that exp rounds
  below1. Source float alpha1behaviour from012is not contradicted or re-proved.
- This **proposes** the missing real phase/EMA state model on current main's B
  definitions. It is not an equality to a pre-existing main phase-state model,
  integration into main, independent adoption, universal Python/float FFI,
  closed-loop locking, full N12sharp ONband or freezing certificate.

## Reproduce / handoff

In a scratch current-main gate project with its prescribed Lean/Mathlib, put the
accepted010/011files and own013/014candidate files on the import path, compile
those dependencies unchanged, then use the commands below. Accepted dependencies:
[HistoryBuffer](cycle_011/proposal/HistoryBuffer.lean),
[PhaseIncrement](cycle_011/proposal/PhaseIncrement.lean). Own candidate dependencies:
[PhaseCoherenceBridge](cycle_013/PhaseCoherenceBridge.lean),
[TrajectoryInvariants](cycle_014/TrajectoryInvariants.lean).

```text
export LEAN_PATH="$PWD:$(lake env printenv LEAN_PATH)"
# use the project-prescribed lean binary, in this dependency order
for f in AIEFGateCore/GateMap AIEFGateCore/K3 AIEFGateCore/RedTeam \
  AIEFGateCore/EngineWitness AIEFGateCore/MatrixForm AIEFGateCore/Capacity \
  HistoryBuffer PhaseIncrement PhaseCoherenceBridge TrajectoryInvariants; do
  lean --root=. -o "$f.olean" "$f.lean" || exit 1
done
lean --root=. ClosedLoopCore.lean
```

No main/pinned source edited. No008/009, rate-law, CI, entrypoint, uploader,
chronicler or competing003port work. No remote branch/push/PR/contact/upload/merge.

**Observed execution-clock record:** clean model compile began
2026-11-10T12:57:24.753970Z; exact negative runs span13:03:58Z–13:17:03Z.
Own temporary setup was removed after checks (62953regular entries,
6032871219logical bytes,15measured symlinks). No unrelated-cache audit/deletion
claim. [STATE.json](STATE.json),[CLAIM_LEDGER.csv](CLAIM_LEDGER.csv) and
[EVIDENCE_INDEX.json](EVIDENCE_INDEX.json) are refreshed for015; old reports/
scientific evidence preserved and old unrecorded execution dates not invented.


**Requested review:** assess this one concrete recursion and its connections,
especially NEW-C/R-before-B, NEW-gated-B-before-phase and append-NEW-θ clocks.
Future work must exploit properties of this actual constrained phase/EMA evolution
rather than assuming the desired bands. Another Continue must refresh main,
ERRATA, merged/open PRs and feedback; no016work has started.
