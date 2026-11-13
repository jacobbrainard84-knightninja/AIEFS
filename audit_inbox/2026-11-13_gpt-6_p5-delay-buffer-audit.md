# GPT-6 review — P5 delay-buffer coverage and branch documentation

- Agent: GPT-6
- Date: 2026-11-13 (Europe/Tirane)
- Main reviewed: `a559e0d30458bb01989ac47225675d6baec518b8`
- Candidate reviewed: `research/lean-gate-p5@ab18b068e1560b7d6d8005f42ed4d22c7097c8c2`
- Inbox branch before deposit: `5d91c098ca3bcba7ea9c40e825bbbcb0ca7f9065`
- Scope: P5 history/phase/coherence candidate, actual Python history-buffer integration coverage, P5 docs and current CI wiring.
- Review method: static source inspection, branch comparison and GitHub Actions metadata. **No Lean build, Python test suite, or mutation script was run by GPT-6.** The cited GitHub action runs are reported as observed CI metadata, not reproduced locally.

## 1. Main's engine step-order tests do not exercise the production delay length

**Classification: material test-coverage gap; not evidence of an existing runtime defect.**

The frozen production constants in `aief_experiment_engine_v1.py` (blob `0d116e83a0d2f6b3f6be0e21d8a730c0aec3b689`) are `FROZEN_DT = 0.01` and `FROZEN_TAU = 0.5` at lines 63–65, so the engine's `delay_steps = round(tau / dt)` at lines 171–174 is **50**. The exact divisibility check is at lines 232–237.

The actual Python buffer contract is:
- `initialize_state` creates `delay_steps + 1` separate copies of the initial phase vector (lines 710–718);
- `compute_R` reads `state.history[0]` (lines 729–740);
- the phase coupling also reads `state.history[0]` (lines 830–835);
- each step appends the new phase and pops one oldest entry if the list exceeds `delay_steps + 1` (lines 841–844).

The new engine tests in `research/lean_gate/tests/test_engine_step_order.py`, blob `ea303c175cf102cee736fc5a95f1687e65ee9b1b`, do execute the real `advance_state` implementation. However, their common helper at lines 35–41 hard-asserts `c.delay_steps == 1`; all four probes (test functions at lines 61, 81, 100 and 116) therefore use a **one-step queue**. They cover useful first-step order, oldest-slot read, dt scaling and old-B carry, but not a 51-element production queue or its repeated aging across the 50-step delay.

The P5 Lean queue theorem is correctly more general at the mathematical level: `HistoryBuffer.lean`, blob `09ce8458b7a70f14097da05513e271e28e412b86`, proves `historyTrace_index`, `historyTrace_oldest` and `historyTrace_newest` for arbitrary `d`. `PhaseIncrement.lean`, blob `35e442fe9d3469ee3ad374934c10e91b357330ad`, also states the delayed increment for general `d`. But these are abstract Lean sequence functions; the module scope explicitly does not claim Python list/aliasing equivalence. The P5 specification itself says its probes use only `D ∈ {1, 2}` (SPEC blob `0db153c5bb1d306b9330c6fb78226794b741aac6`, lines 945–946).

**Why this matters.** The d=1 engine probe distinguishes the oldest slot from the current phase for a hand-built two-slot history. It does not check that the actual Python list preserves the correct slot over 50 successive append/pop operations, nor that the startup-to-live-delay boundary lands at the right step for the frozen production configuration. The general Lean theorem is not a substitute for that implementation check; the candidate's own scope statement says so.

**Recommended independent test additions (on a branch from current main, not in this inbox note):**
1. Add a production-delay configuration probe with `dt=0.01`, `tau=0.5`, asserting `delay_steps == 50`, initialization length 51, and the one-step use of a deliberately non-constant 51-entry history (to distinguish slot 0 from slot 1 and the newest slot).
2. Add a 51-step buffer-aging/startup probe. Before each call, assert that the oldest slot is the phase at `max(0, n-50)`; after each call, assert that the append/pop operation leaves length 51, advances the oldest slot exactly once when due, and leaves the newest slot equal to the newly appended phase. Include an explicit check of the first live delayed value at the (n=50) boundary.
3. Keep the d=1 probes: they isolate individual update-order errors and are valuable, but label them as unit-delay probes rather than production-delay coverage.

These checks would exercise the real Python buffer without claiming a proof about float64 phase locking.

## 2. P5 documentation is stale about its own mutation check and mutant inventory

**Classification: confirmed documentation drift on the P5 branch.**

At P5 tip `ab18b068e1560b7d6d8005f42ed4d22c7097c8c2`:

- `.github/workflows/lean.yml`, blob `b36b3e2ca396e89ac62d4ad7e8ff13deab148bc7`, lines 90–102, runs `python3 research/lean_gate/lean_mutation_check.py` on the `AIEFGateCore` matrix row.
- The P5 CI run [42962654415](https://github.com/jacobbrainard84-knightninja/AIEFS/actions/runs/42962654415) reports the `lean (AIEFGateCore)` job, `check_lean_gate.sh` and `Lean-gate mutation check (AIEFGateCore only)` step successful.
- Nevertheless, `research/lean_gate/SPEC_P1_gate_identities.md` blob `0db153c5bb1d306b9330c6fb78226794b741aac6`, §11.6 line 1062, says the mutation check is not run in CI.
- `lean/AIEFGateCore/README.md` blob `7b7bda1dfa2161b156741290406663478ad42e19`, lines 52–59, still describes only 23 statement mutants, P5 M37–M52 as 16 definition mutants, and one expected known survivor. In the same P5 branch, `research/lean_gate/lean_mutation_check.py` blob `ed38a415d9d2d3c4b8a3867d6fb9312a43c7eb0a` has M57–M58 at lines 314–321, a 20-entry `DEF_MUTANTS` list beginning at line 358, and `KNOWN_SURVIVORS = []` at line 450. The SPEC confirms 38 statement + 20 definition mutants = 58 total at lines 950–953 and records 58/58 at lines 1086–1093.

**Disposition.** These are documentation-only discrepancies; they do not undermine the observed CI success or establish a Lean theorem defect. Refresh the P5 README and §11.6 as part of the necessary merge refresh so the documentation reports the live 58-mutant suite and acknowledges that the mutation check is already wired in CI. Preserve the genuinely open item: no Lean-side statement-hash pin is implemented.

## 3. Branch freshness / scope

The comparison of `main` and `research/lean-gate-p5` at review time is `main@a559e0d` versus `p5@ab18b06`: the P5 branch is **4 commits ahead and 3 behind**, with merge base `75f2b7405ec6eeae36bf20a5e88bedd997788d83`. It therefore predates PR #30 on main. The README/spec drift should be reconciled during that merge refresh, with a fresh delta review before any PR.

P5's mathematical work remains correctly scoped as exact-real sequence/EMA components. It does not prove the Python buffer implementation, the clipped/projected B trajectory, float64 equivalence, or phase locking. The missing production-delay probe is a practical next implementation check, not evidence that the present engine's history indexing is wrong.

**UNVERIFIED INPUT — not independently triaged or promoted.**
