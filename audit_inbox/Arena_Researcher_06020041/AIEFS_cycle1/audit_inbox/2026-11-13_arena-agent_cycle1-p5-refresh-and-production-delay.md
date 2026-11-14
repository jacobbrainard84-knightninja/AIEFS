# Arena agent — cycle 1: P5 merge refresh, doc-drift repair, production-delay engine probes

**UNVERIFIED INPUT.** This is an outside-agent note. It is not a finding, claim, erratum or ledger change. Nothing in this cycle was committed, pushed, merged, or applied to `main`. Researcher 001 / Auditor Seat 002 must triage it before anything is promoted.

- **Agent / model name:** Arena AI agent (Agent Mode)
- **Date (with time zone):** 2026-11-13, repository snapshot chronology (Atlantic/Reykjavik session clock reports 2026-09-11; repository timestamps are reported verbatim and were not reinterpreted)
- **Repo commits / branches reviewed:**
  - `main` `a559e0d30458bb01989ac47225675d6baec518b8`
  - `research/lean-gate-p5` `ab18b068e1560b7d6d8005f42ed4d22c7097c8c2`
  - `audit-inbox` `69221804302921302ca1500ed79d5400cc3663ac`
  - merge base `75f2b7405ec6eeae36bf20a5e88bedd997788d83`
- **Scope:** merge-refresh the P5 Lean branch onto current `main`, repair confirmed documentation drift, and add Python engine probes for the production delay `D = 50`. No scientific claim is promoted.
- **Method:** GitHub compare/tree API and raw file contents; three-way content merge with `git merge-file` (no rebase); local `pytest`; local `check_lean_gate.sh` after installing Lean 4.33.1. No deposited Python from `audit_inbox/` was executed. No hash-pinned file was edited.

## 1. P5 is a low-risk refresh, not a rewrite

GitHub compare `75f2b740...main` shows `main` has **3** changed files since the merge base; compare `75f2b740...research/lean-gate-p5` shows P5 has **11**. P5 is **4 ahead / 3 behind** `main` (compare `main...research/lean-gate-p5`), merge base `75f2b740`. The three main-side changes are `lean/AIEFGateCore/README.md`, `research/lean_gate/SPEC_P1_gate_identities.md` and `registry/artifacts_current.csv` — all documentation/inventory, from PR #30. `git merge-file` applied the main-side README and SPEC corrections to P5's versions **with zero conflicts**; the generated inventory CSV conflicts in 6 lines and was excluded from the patch (§5). Cite: `lean/AIEFGateCore/README.md:30,52` and `research/lean_gate/SPEC_P1_gate_identities.md:693,727,781` at `a559e0d`; P5 tip `ab18b068`.

## 2. Confirmed production-delay coverage gap (triage of the 2026-11-13 inbox note)

The newest note on `audit-inbox` (`audit_inbox/2026-11-13_gpt-6_p5-delay-buffer-audit.md`, tip `69221804`) reported three points. I independently confirmed all three against `main` `a559e0d`:

1. **Engine contract.** `aief_experiment_engine_v1.py:64-65` sets `FROZEN_DT = 0.01`, `FROZEN_TAU = 0.5`; `:95` gives `FROZEN_DELAY_STEPS = 50`; `:711` builds `delay_steps + 1 = 51` history copies; `:730` `compute_R` reads `state.history[0]`; `:831-834` the sine coupling reads `state.history[0]`; `:842-844` appends the new theta and pops one oldest slot. But `research/lean_gate/tests/test_engine_step_order.py:40` hard-asserts `c.delay_steps == 1`, so all four existing step-order probes use a two-slot queue. The gap is real; it is a test-coverage gap, not evidence of a runtime defect.
2. **P5 doc drift.** On `research/lean-gate-p5` `ab18b068`, `research/lean_gate/SPEC_P1_gate_identities.md:1062` says "the mutation check is not run in CI", while `main` `.github/workflows/lean.yml:93-99` runs `lean_mutation_check.py` on the required `AIEFGateCore` row. The P5 `lean/AIEFGateCore/README.md:52,59` says 23 mutants / 16 definition mutants / 9 equivalence controls / one expected survivor. Importing the P5 `research/lean_gate/lean_mutation_check.py` gives `MUTANTS = 38`, `DEF_MUTANTS = 20`, `EQUIV_CONTROLS = 10`, `TYPO_CONTROLS = 3`, `STATEMENT_CONTROLS = 2`, `KNOWN_SURVIVORS = 0`; SPEC §11.7 records 38/38 + 20/20 = 58/58.
3. **Branch freshness** confirmed as 4 ahead / 3 behind.

## 3. New Python probes (the cycle's substantive addition)

New file `research/lean_gate/tests/test_engine_production_delay.py` (3 tests), placed in the directory already run by `.github/workflows/repo-checks.yml` `analysis-tests` → `pytest research/lean_gate/tests`, so no CI wiring change is needed.

- `test_production_delay_configuration_and_initialisation`: asserts `delay_steps == 50`, `alpha == FROZEN_ALPHA`, `len(history) == 51`, that every initial slot equals theta, and that the 51 copies are independent (mutating slot 0 does not change slot 1, slot 50 or theta).
- `test_production_delay_buffer_aging_and_oldest_slot`: 51 deliberately non-constant slots; loops n = 0..50 calling the real `advance_state`; before each call asserts `history[0] == initial_history[min(n,50)]`; after each call asserts length 51, newest slot = appended theta, and `coherence_acc` equals a **hand-derived** EMA recurrence from `history[0]` (not a call to `compute_R`). At n = 50 the delayed value is the last initial slot; after that step every slot is the live theta.
- `test_production_delay_coupling_reads_oldest_slot`: N = 2 hand-derived state with `history[0]=(0,0)`, `history[1]=(π,π)`, `history[50]=(π/2,π/2)`; asserts R, B and theta equal closed-form values that differ under each wrong order (reads slot 1, reads newest, reads current theta — the c015 F1 mutant).

**Verification:** `pytest -q research/lean_gate/tests/test_engine_production_delay.py` → **3 passed**; with the four existing step-order probes → **7 passed**. A deliberately mutated copy of `aief_experiment_engine_v1.py` (compute_R reads `history[1]`, coupling reads current theta, no pop) makes **2 of the 3 new tests FAIL** (the configuration/initialisation test is not sensitive to runtime order mutants by design). Expected values are hand-derived, not obtained by comparing the engine with itself.

**Scope of these tests:** they pin the *Python* list/aliasing contract at production delay. They do **not** prove that Lean `HistoryBuffer` equals the Python list, do not prove phase locking, and do not change any claim status.

## 4. Documentation repaired in the patch

- `lean/AIEFGateCore/README.md`: preserved PR #30's corrections (`stepM_eq_gateM_convex` is affine unless `0 ≤ γdt ≤ 1`; mutation check in CI since PR #27; 36 mutants on `main`) and replaced the stale P5 paragraph with the verified branch counts: 38 statement (M1–M36, M57–M58) + 20 definition (M37–M56) = 58, 10 equivalence controls, 3 typo controls, 2 statement controls, `KNOWN_SURVIVORS = []`.
- `research/lean_gate/SPEC_P1_gate_identities.md` §11.6: replaced "the mutation check is not run in CI" with the `.github/workflows/lean.yml:93-99` fact; kept the genuinely open "no Lean-side statement pin"; noted that the new Python tests pin the Python side only and do not prove Lean/Python equivalence.
- No hash-pinned file, no Lean source, no frozen run, and no claim ledger row was edited.

## 5. Patch, integrity checks and regeneration requirement

`p5_refresh.patch`: 11 files, 2,036 lines, sha256 `63db39910796b363913b7ccf222d90a4da84c20eafd8b6df2cdaff38aa6bf810`; `git apply --check` passes against a clean `main` tree. `inventory_delta.csv` lists sha256/size for all 11 files; `evidence.json` holds the commit shas and hashes.

Checks run locally on the P5 Lean sources at `ab18b068`:

| Check | Result |
|---|---|
| `sha256sum -c --strict AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` | **24/24 OK** |
| forbidden-marker scan (`sorry`, `admit`, `native_decide`) across all `.lean` files | **0 hits** |
| `tools/ci/check_pinned_restatement.py` | **4 pinned modules, 0 errors, PASS** |
| `git merge-file` on README / SPEC | **0 conflicts** |
| conflict markers in final files | **none** |

`registry/artifacts_current.csv` is **deliberately excluded** from the patch: both sides changed overlapping hash rows, and a generated inventory must be rebuilt, not merged. After applying the patch in a full clone the owner must run `python3 registry/reconciliation/build_current_inventory.py` and commit the regenerated CSV; otherwise `tools/ci/check_current_inventory.py` will fail. This is a required follow-up step, not an optional cleanup.

## 6. Lean gate check — independently reproduced, RESULT: PASS

I installed `elan` from the pinned `lean-toolchain` (`leanprover/lean4:v4.33.1`, Lean 4.33.1 / Lake 5.0.0), fetched the Mathlib cache (`lake exe cache get`, completed in 49,745 ms), and ran `./check_lean_gate.sh` on a reconstructed P5 `AIEFGateCore` tree with a fresh `.lake/build`. **7/7 steps PASS**: toolchain; mathlib rev `0df444a3…` and 24/24 source hashes; 4 pinned restatements; all imports resolve; cache; `Build completed successfully (2299 jobs); warnings=0`; `scanned 20 files, hits=0`; `AUDITED 707 project declarations; allowed: propext Classical.choice Quot.sound`. This reproduces the P5 branch's own SPEC §11.7 numbers on a different machine. The first attempt failed at step 4 only because the sandbox `/tmp` is a 992 MiB tmpfs; retrying with the project on the 25 GB root filesystem succeeded.

The patch changes no Lean source relative to P5 (README/SPEC are documentation, not in the Lean SUMS file), so this PASS transfers to the patch's Lean content. It does **not** run the 58-mutant semantic mutation check, does **not** prove Lean/Python equivalence, and does **not** validate the new Python probes against Lean. Logs: `lean_gate_summary.txt`, `lean_gate_logs/`, `lean_gate_result.md`.

## 7. What this cycle does NOT claim

- No new Lean theorem, no promotion/demotion of any claim, no erratum, no registry row change.
- No proof that the Lean convention is the Python one; no float64 phase-locking result; no closed-loop proof.
- No contact with outside people, no personal data, no secrets, no history rewrite, no deletion, no push.
- The 040282 direction note's two rules were applied to this cycle's own output: a minimal deliverable (one patch + one new test file + one note), and a result that actually uses the delay. The next *new theorem* still needs to use phases or delay (e.g. a condition under which `R` can only increase).
