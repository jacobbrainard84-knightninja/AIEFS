# Arena agent — cycle 2: port of c016 `CoherenceMotion.lean` (P5 branch)

**UNVERIFIED INPUT.** Outside-agent work; not a finding, claim, erratum or ledger change. Nothing was committed, pushed, merged, or applied to `main`. Researcher 001 / Auditor Seat 002 must triage it first.

- **Agent / model name:** Arena AI agent (Agent Mode)
- **Date (with time zone):** 2026-11-13, repository snapshot chronology (Atlantic/Reykjavik session clock reports 2026-09-11; repository timestamps are reported verbatim)
- **Repo commits / branches reviewed:** `main` `a559e0d30458bb01989ac47225675d6baec518b8`; `research/lean-gate-p5` `ab18b068e1560b7d6d8005f42ed4d22c7097c8c2`; `audit-inbox` `69221804302921302ca1500ed79d5400cc3663ac`; c016 deposit at `audit-inbox` commit `0f189d0`; base for this cycle is the Cycle-1-refreshed patch (`p5_refresh.patch`, sha256 `63db3991…`).
- **Scope:** port Researcher 040282 cycle 016 into the P5-refreshed `AIEFGateCore`, wire one mutant, reproduce the Lean gate and the mutation suite locally. No scientific claim is promoted.
- **Method:** GitHub raw/tree API; a reconstructed minimal P5 project; Lean 4.33.1 installed from the pinned `lean-toolchain`; `lake exe cache get`; `check_lean_gate.sh`; full `lean_mutation_check.py`; `pytest research/lean_gate/tests`. No deposited Python from `audit_inbox/` was executed. No hash-pinned or frozen file was edited.

## 1. What was ported

`audit_inbox/2026-11-08_researcher-040282/researcher_040282/cycle_016/CoherenceMotion.lean` (14,699 bytes, md5 `079a72f3…`), rated ADOPT WITH NOTES by Auditor Seat 002 in `audit_inbox/2026-11-11_auditor-seat-002_lean-candidate-reviews/2026-11-11_audit_040282_c012_c016.md`. It builds on unmodified P5 `PhaseCoherence.lean` and proves the one-step EMA / reported-`R` movement bounds, including `|R_{n+1} − R_n| ≤ min(1, 2(1−α))` under `0 ≤ α ≤ 1` and `∀ i j, ‖C0 i j‖ ≤ 1`.

At `aief_experiment_engine_v1.py:64-65,85-86` (`dt = 0.01`, `T_window = 17.50291715…`), `α = 0.99942883…`, so `2(1−α) = 0.00114…`; 0 → 1 needs ≥ ~875 steps (≈ 8.75 time units). This is the first quantitative statement about `R` along the real step.

**The auditor's limitation is carried into the module docstring verbatim:** the proof is the triangle inequality on an EMA with unit-norm inputs, uses **no phases, delay, `ω` or `B`**, and is a *speed limit, not dynamics*. Node-uniform probes do not exercise symmetrisation; the bound is exact reals, not float64; the P5 engine convention is hand-checked, not proved against Python. No phase locking, no closed-loop claim. `AUD-RATELAW stays UNEXPLAINED`.

## 2. Differences from the deposit

- Standard Apache/SPDX header and scope docstring; module docstring moved **after** the `import` (Lean requires imports first — the first compile attempt failed at `CoherenceMotion.lean:30` with "invalid 'import' command").
- 21 trailing `#print axioms` lines removed (step 7 of `check_lean_gate.sh` prints them).
- Nine long-line / whitespace lint issues and three unused binder names fixed; the file now builds with **0 warnings**. All are formatting-only; statements and proofs are unchanged.
- One theorem added: `false_trace_step_abs_le_half`, a proved negation of the halved one-step bound, used as the negative control for mutant M59.
- Wiring: `lean/AIEFGateCore/AIEFGateCore.lean` gains `import AIEFGateCore.CoherenceMotion`; `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` regenerated (24 → 25 entries); README and SPEC §11.6/§11.8 updated; no hash-pinned or frozen file touched.

## 3. Mutant M59 and count pins

`research/lean_gate/lean_mutation_check.py` gains `M59_coherence_motion_half_bound`: replace `≤ 2*(1-alpha)` with `≤ (1-alpha)/2` in `trace_step_abs_le`, refuted by `CoherenceMotion.false_trace_step_abs_le_half` (build rejection + step-(b) negation + term-specificity control all required by the harness). Suite is now **39 statement + 20 definition = 59 mutants**. `test_lean_gate_p4b.py:119` pins `len(names) == 39`; `test_lean_gate_p5.py:32-34` pins `N_STATEMENT_MUTANTS = 39` and `TOTAL_MUTANTS = 59`. The 58/58 result in SPEC §11.7 is retained as a historical record and superseded for the current tree by §11.8.

## 4. Local verification

| Check | Result |
|---|---|
| `./check_lean_gate.sh` (Lean 4.33.1, Mathlib cache, fresh `.lake/build`) | **PASS 7/7**. Step 2: 25/25 SUMS, 4 pinned restatements PASS; step 3: all imports resolve; step 5: `Build completed successfully (2300 jobs); warnings=0`; step 6: `scanned 21 files, hits=0`; step 7: `AUDITED 739 project declarations; allowed: propext Classical.choice Quot.sound`. |
| `lake env lean AIEFGateCore/CoherenceMotion.lean` | 0 warnings, 0 errors. |
| `pytest research/lean_gate/tests` | **70 passed** (Cycle-1 production-delay probes + updated 39/59 count pins). |
| Isolated M59 verification, using the harness's own `lean()` machinery | **PASS**: (a) mutated statement fails to build with a `REAL PROOF FAILURE`; (b) `CoherenceMotion.false_trace_step_abs_le_half H` elaborates as `¬ prop`, `#print axioms` = `[propext, Classical.choice, Quot.sound]`; (c) the same term fails on the unmutated statement (term specificity). |
| `git apply --check c016_port.patch` | OK (8 files, 534 lines). |

**Not completed — stated plainly:** the **full 59-mutant suite was not run to completion locally**. Every `lake env lean` call reloads the ~2,300-module Mathlib import graph (~2 min per call in this 2 GiB sandbox); a 49-minute run was stopped before finishing. This is NOT a claimed pass. The full suite remains a CI/owner step: `.github/workflows/lean.yml:93-99` runs `lean_mutation_check.py` on the required `AIEFGateCore` row. M59 was verified in isolation with the harness's own build / refutation / term-specificity checks. The `OPENS` addition (`open AIEFGate.CoherenceMotion (rTrace)`) was required because the generated refutation file lives in namespace `AIEFGate`; without it the M59 refutation failed with `Unknown identifier 'rTrace'` — a real defect found and fixed by this cycle.

Logs: `lean_gate_summary.txt`, `lean_gate_logs/`, `verify_m59.log`.

## 5. What this cycle does NOT claim

- No phase/delay-dependent theorem was added. The 040282 direction note's second rule is explicitly **the next cycle's target**: candidate `input_constant_after_lock` (phase increments vanish from `N` ⇒ `coherenceInput` constant for `n ≥ N + d`, via `Phase.delayed_input_step`) plus a monotone-up condition for `R`.
- No proof that the Lean convention equals the Python one; no float64 phase-locking result; no closed-loop proof.
- No claim status change, no erratum, no registry row change, no push, no deletion, no history rewrite, no personal data, no secrets.

**Compile command:** `cd lean/AIEFGateCore && SKIP_CACHE=1 ./check_lean_gate.sh` (or `lake build AIEFGateCore.CoherenceMotion` for the single module).

**Deliverables:** `AIEFS_cycle2/` — `ONE_PAGE_NOTE.md`, `DELTA_AUDIT.md`, `c016_port.patch` (8 files, `git apply --check` OK), `files/`, `inventory_delta.csv`, `evidence.json`, Lean gate and mutation logs. `registry/artifacts_current.csv` is excluded; regenerate with `python3 registry/reconciliation/build_current_inventory.py` in a full clone after applying.
