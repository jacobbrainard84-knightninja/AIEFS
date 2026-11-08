# Researcher 040282 — self-directed AIEFS research

Say **Continue** to start the next bounded cycle. I will read saved state and
feedback, select the next useful dependency, preregister its domain/falsifiers,
perform meaningful research and adversarial checks, compile Lean when appropriate,
and deliver a standalone Markdown audit for owner upload. No new technical
assignment is necessary.

This is user-triggered work, not claimed background activity between turns.
I do not contact other agents, push/submit files, edit frozen/team-owned
sources, or promote registry claims without separate authorization.

## Persistent workflow

- `WORKFLOW.md` — procedure, evidence labels, scope and publication boundaries.
- `STATE.json` — actual last outcome and immediate resumption action.
- `RESEARCH_QUEUE.md` — chosen next dependency and revisable later candidates.
- `CLAIM_LEDGER.csv` — individually scoped statements and evidence/status.

Compiler success, exact finite checks, floating-point source checks, independent
review, source execution linkage, integration, and publication stay separate.
Self-red-teaming is not Auditor Seat 002 approval.

## Latest local contribution — Cycle 003

**Upload this single file:**

`2026-11-07_researcher040282_003_weight-update-bridge.md`

Its critical Lean/checker code is entirely inline. Optional supporting archive:
`researcher040282-cycle003-weight-update-bridge.zip`.

The new compiled module has **44 declarations**, including helper lemmas:

- clipped zero-diagonal proposal row envelopes;
- applied factors on both global guard branches, with epsilon retained;
- division-free capacity bounds and ratio bounds only at positive rows;
- positivity/row invariance from the first step and the H0 exception at time zero;
- exact matrix-update-to-edge recurrence;
- conditional existential per-edge OFF/ON statements and tail-start variants,
  composed with the existing upstream scalar comparison core.

The package freshly recompiles **22 prior local declarations and five upstream
ones**. Those are reused dependencies, not new results/authorship credit. All
accepted printed axiom footprints are restricted to `propext`, `Classical.choice`,
and `Quot.sound`, with no warnings/errors and complete coverage.

Observed controls: **17 intended outcomes**, five positive and twelve negative;
384 exact Fraction property cases. Separate actual-engine adaptive weight-step
comparisons: **24 passed**, 4 active/20 inactive, maximum absolute error
`2.7755575615628914e-17` against fixed absolute `5e-15`, relative zero.
Those source comparisons replace compute_R by a controlled driver and test only
weights, not physical coherence/EMA/delay evolution. All five critical files were
also actually extracted from the single Markdown into a fresh directory: all
17 controls and 24 source comparisons passed again. This is local self-
reproduction, not independent-seat review.

**Not established:** actual future coherence bands, full Python/float64 linkage,
closed-loop phase-locking, gated-OFF composition, complete network freezing,
explicit freeze times, delayed/EMA dynamics correctness, or stability.
The conditional ON/OFF conclusions do not supply their own infinite-tail bands.

**Status:** local self-red-team; independent review, owner upload, publication,
and integration are unconfirmed. No remote source change or bot contact occurred.

## Reproduction

The audit gives extraction and complete public dependency commands. With the
recorded trusted Lean/Mathlib available, from `cycle_003/`:

```bash
export R040282_MATHLIB=/absolute/path/to/pinned-mathlib4
export R040282_LEAN_BIN=/absolute/path/to/compiler/bin/lean
# Optional: export R040282_CACHE=/owned/scratch/directory
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python check_cycle.py > cycle_checks.log 2>&1
```

The compiler path needs a sibling `lake`. The proof harness uses Python's standard
library, checks the recorded toolchain/Mathlib, freshly compiles its two local
proof dependencies, and compiles each bridge/control in a fresh directory. Run
with assertions enabled. Dependency/import failures are blockers, not successful
mathematical rejections. This is a bounded supplied-file checker, not secure
intake of arbitrary Lean code or a replacement for the receiving seat's CI.

Exact controls without Lean:

```bash
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python check_cycle.py --exact-only
```

Optional source comparison, with NumPy/pandas and a reviewed engine source:

```bash
export R040282_AIEFS_ENGINE=/absolute/path/to/reviewed/aief_experiment_engine_v1.py
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python compare_source.py
```

`build_packet.py` assembles the audit from actual source/results.
`one_file_reproduce.py` extracts its critical blocks and actually reruns the
proof/exact checker and controlled-source checker with the public dependencies.
`build_packet.py --package` creates the optional bundle once final records exist.
The copied `FreezeCore.lean` is an upstream reproduction fixture, not something
to duplicate as new authoritative definitions during integration.

Lean/compiler and Mathlib binaries/cache are disposable and excluded from saved
snapshots. Their loss was observed at this cycle's start. Sources, setup helpers,
metadata and logs persist; inspect availability before reinstalling, and preserve
prior-cycle evidence rather than overwriting it.

## Next selected work

Complex EMA unit-disk preservation, reported-coherence symmetry/diagonal/range,
and resulting drive bounds, followed by exact fixed-input recurrence. This is a
new actual-source component, not a claim that fixed input proves coupled locking.
Feedback and already-landed work are checked before proceeding.

## Earlier packets, preserved separately

- **001:** `2026-11-07_researcher040282_gate-foundations.md` and
  `researcher040282-gate-foundations.zip`. Paper/exact groundwork and 96 isolated
  eta=mu=gamma=0 engine/helper comparisons; not compiled at delivery.
- **002:** `2026-11-07_researcher040282_002_guarded-capacity-lean.md` and
  `researcher040282-cycle002-guarded-capacity.zip`. 22 compiled finite-map
  declarations, nine controls, actual one-file reproduction. Does not silently
  upgrade every earlier continuity, branch-linearity, or rate-law observation.

Historical ledger references remain references to those separate packets; the
latest support ZIP is not intended to republish every earlier audit/data file.
