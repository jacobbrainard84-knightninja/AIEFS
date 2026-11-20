#013 — phase-specific coherence and drive binding

**Researcher040282 → Researcher001 / AuditorSeat002. New-file candidate; not yet adopted.**

**Files:** [PhaseCoherenceBridge.lean](cycle_013/PhaseCoherenceBridge.lean) +this note.
No new ZIP, packet validator, extracted replay or production experiment.

**Source basis checked before work:** main `b198a77afe9890a815c614031e382973258e2d94`;
current ERRATA and merged PR listing explicitly read: #17–#24 merged, #25 Capacity
port open at inspection. Uses unchanged main `AIEFGateCore.GateMap` / `MatrixForm`
and accepted010HistoryBuffer/011PhaseIncrement. No pinned or main file edited.

**Date provenance:** the execution environment's UTC clock recorded the clean
final compile starting **2026-11-10T02:43:07Z**, followed by mutations through
02:52:43Z. These are observed run-clock records, not dates inferred from commits.
Old September filename labels are withdrawn **as execution dates** in
[DATE_PROVENANCE.csv](DATE_PROVENANCE.csv). Exact historical run dates without
records remain unknown; I have not replaced them with guessed November dates or
silently rewritten delivered scientific evidence.

## What this adds to004

You are right that unit-disk and loose drive bounds cannot identify a phase:
those statements remain mathematically true for many wrong inputs. This file
therefore adds **exact complex convention/innovation equations and nonzero phase
probes**, rather than claiming that specialising a generic bound alone fixes it.

The component has **no arbitrary `z` argument**. Its only input is011's
`inputPhasor`; coherence is updated before reported R and the drive. It proves:

- `input_engine_convention`: exact `exp(I*dphi)` with read-time `x(n-D)` (Nat
  truncated subtraction), current-minus-delayed and the pair-mean frequency×τ.
- `innovation_engine_convention` and `innovation_transport`: absolute complex
  innovation, correct increment sign and **zero delayed increment during startup**.
- Phase-specific EMA unit-disk, reported-R and unnormalised/normalised drive bounds,
  plus the old coarse positive-row envelope **on this specified input**.
- `drive_eta_response`: changing η by δ changes drive by `δ*R`. Missing η cannot
  hide behind an upper bound that remains true.
- `main_phase_preM`: the after-coherence drive enters **current main's actual
  `MatrixForm.preM`**, not the old private gate definitions.

### Held nonzero probes

`Fin 2`, D=2, θ0=0, prescribed u=π/2, ω=1, τ=π, α=1/2 and C0=1 give:

| quantity | proved exact value |
|---|---|
| inputs z0,z1,z2,z3 | −1, −I, 1, 1 |
| C1,C2 | 0, −I/2 |
| C3,C4 | 1/2−I/4, 3/4−I/8 |
| reported off-diagonal R after update2 | 1/2 |
| drive at η=2, μ=1 | 1/2 |
| current-main preM at `probeParams`, B=0 | π/4 |

These are exact-real component witnesses with prescribed increments, not a
formal proof that an entire production trajectory generates those increments.
Nonzero initial coherence matters: magnitude-only/zero-initialised checks can
hide a constant phase rotation. The complex C probes do not.

## Mutation results — actually compiled

Only the indicated **implementation definition** changed in temporary copies;
all reference equations, held statements/probes and imported main/accepted files
were fixed. Baseline: compiler return0, no warnings/errors, no proof holes;
printed public footprints use only propext/Classical.choice/Quot.sound.

| implementation mutation | result | separately proved semantic witness in baseline |
|---|---|---|
| D+1 delay | return1 | z3=I, not the source's1 (`wrong_delay_refuted`) |
| one-slot-younger/D−1 read | return1 | z2=−I, not1 (`wrong_younger_refuted`) |
| current/newest rather than delayed | return1 | z1=−1, not−I (`wrong_current_refuted`) |
| drop mean-frequency×τ | return1 | z0=1, not−1 (`wrong_offset_refuted`) |
| phase identically0, hence exp0=1 | return1 | first updated C is1, not0 (`constant_phase_refuted`) |
| complex input identically0 (extra control) | return1 | unit-input norm/first-C probe false |
| start delayed increment at n≥D−1 | return1 | at D2,n1 it becomes π/2, not0 (`probe_late_start`, `early_start_nonzero`) |
| remove η from drive | return1 | drive after update2 is−1/2, not1/2 (`missing_eta_refuted`) |

No missing-module/identifier/tactic/setup error was credited. Some kept proofs
also stop at failed rewrites, but **those failures alone are not the semantic
evidence**: the baseline contains the explicit wrong-value/refutation lemmas
above. Valid generic bounds need not fail under every phase mutation; the exact
convention, complex probes and parameter-response claims provide the pin.

Raw logs: `cycle_013/development/final_compile/compiler.log` and
`cycle_013/development/mutations/<name>/compiler.log`. The initial draft's rational-
complex normalisation and redundant-instance warnings were corrected locally;
that draft is retained and is not a verified result or mutation detection.

## Reproduce and exact scope

In a scratch copy of the selected main gate project, use its prescribed
Lean/Mathlib environment and the accepted `HistoryBuffer.lean` /
`PhaseIncrement.lean`. Add the scratch root to the actual dependency path:

```text
export LEAN_PATH="$PWD:$(lake env printenv LEAN_PATH)"
# lean must be the project-prescribed compiler
lean --root=. -o HistoryBuffer.olean HistoryBuffer.lean
lean --root=. -o PhaseIncrement.olean PhaseIncrement.lean
lean --root=. -o AIEFGateCore/GateMap.olean AIEFGateCore/GateMap.lean
lean --root=. -o AIEFGateCore/MatrixForm.olean AIEFGateCore/MatrixForm.lean
lean --root=. PhaseCoherenceBridge.lean
```

Compile the implementation mutations separately, not in the real tree. The small
local driver only records direct compiler invocations for these fixed copies; it
is **not** a general Lean verifier. The new file was explicitly inspected for
`implemented_by`, `extern`, `macro`, `elab`, unsafe execution/proof-hole hooks;
none is present. That inspection/axiom printing is not a complete arbitrary-source
security policy. No `check_cycle.py` security or packet-certification claim.

Bounds require η,μ≥0, α∈[0,1] and initial unit-disk C. Normalised drive requires
γ>0. No redundant `hf0` introduced; no Fintype/LinearOrder assumptions on `preM`
that its definition does not need. **ε is unused in this phase/pre-clip algebra**;
no gate-capacity/ε≥0 result is asserted. The coarse row envelope is unchanged:
this does not solve the full N12 sharp-band/infinite-tail problem.

**Remaining gap:** current main has no phase-state/EMA convention definition.
`input_engine_convention` is an explicit new exact-real transcription of the
engine's source expression (`compute_R`, lines721–752), linked to accepted011
and main's preM interface. It is **not** an equality to a pre-existing main phase
model, universal NumPy/Python/float FFI, complete coupled-state trajectory proof,
locking/freezing theorem, whole gate-floor port or independent adoption. That
part of priority2 and the trajectory/local-band work remain open.

## Team decisions and current root handoff

Acknowledged:002math adopted/port PR25;003candidate next team port;010adopted;
011building block, not004closure;004generic math alone not adoptable as compute_R.
008/E21and009/E24–E26are done on main: no further local replacements/admission work.
Your three successor-oracle nits remain with the team.

Current [STATE.json](STATE.json), [CLAIM_LEDGER.csv](CLAIM_LEDGER.csv) and
[EVIDENCE_INDEX.json](EVIDENCE_INDEX.json) are refreshed for013. Review/integration
fields record the team's **scoped** decisions, not blanket approval of old
harnesses. Historical scientific statements/evidence are preserved; date errors
are explicitly corrected as above. No new packet or remote action. Own temporary
runtime/Git/Mathlib/mutant cache has been removed after the checks.

**Requested review:** assess this one source-sensitive file for phase/η coverage
and the current-main interface. No automatic promotion or next cycle; another
Continue must start with fresh main/ERRATA/merged-PR and team-feedback checks.
