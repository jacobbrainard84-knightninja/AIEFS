# Arena agent — cycle 3: phase/delay-dependent coherence theorems

**UNVERIFIED INPUT.** Outside-agent work; not a finding, claim, erratum or ledger change. Nothing was committed, pushed, merged, or applied to `main`. Researcher 001 / Auditor Seat 002 must triage it first.

- **Agent / model name:** Arena AI agent (Agent Mode)
- **Date (with time zone):** 2026-11-13, repository snapshot chronology (Atlantic/Reykjavik session clock reports 2026-09-11; repository timestamps are reported verbatim)
- **Repo commits / branches reviewed:** `main` `a559e0d30458bb01989ac47225675d6baec518b8`; `research/lean-gate-p5` `ab18b068e1560b7d6d8005f42ed4d22c7097c8c2`; `audit-inbox` `69221804302921302ca1500ed79d5400cc3663ac`. Base: the Cycle-2 tree (`c016_port.patch`, sha256 `7f3f1cdf…`).
- **Scope:** add a genuinely new Lean theorem that uses the phases or the delay, per the 040282 direction note's second rule. No scientific claim is promoted.
- **Method:** reconstructed minimal P5 project; Lean 4.33.1 from the pinned `lean-toolchain`; `lake exe cache get`; `lake env lean`, `lake build`, `#print axioms`, a semantic mutant, and `check_lean_gate.sh`. No deposited Python from `audit_inbox/` was executed. No hash-pinned or frozen file was edited.

## 1. Motivation

c016 `CoherenceMotion` (Cycle 2) proves `|R_{n+1} − R_n| ≤ min(1, 2(1−α))` but, as Auditor Seat 002 noted, "it never uses the phases, the delay or the weights B, so it would hold for any input at all." The direction note asked that the next result actually use phases or delay, "for example a condition under which R can only go up." This cycle does that.

## 2. New file

`lean/AIEFGateCore/AIEFGateCore/PhaseLockCoherence.lean` (147 lines), namespace `AIEFGate.PhaseLockCoherence`, importing `AIEFGateCore.PhaseCoherence` and `Mathlib.Analysis.Complex.Norm`.

Three theorems:

1. `coherenceInput_constant_after_lock` — if `u n i = 0` for all `n ≥ N`, then `coherenceInput d x0 u omega tau (n+1) i j = coherenceInput … n i j` for all `n ≥ N + d`. Proved from `PhaseIncrement.lean`'s `delayed_input_step` (`:90` in that file) and `delayedIncrement` (`:60`), which reads `u (n - d)` when `d ≤ n`. The proof needs `d ≤ n` and `N ≤ n - d`; the `N + d` boundary is exactly what supplies both. **The proof uses the delay; the failed mutant alone does not establish that the stronger statement is false**: replacing `N + d` by `N` fails with a real `omega` failure (two unsolved goals), not a name/parse error.
2. `coherenceTrace_geometric_of_constant_input` — constant input `z` from `n0` ⇒ `C_{n0+k} − z = α^k (C_{n0} − z)` on `PhaseCoherence.coherenceTrace`. This exact identity permits any real alpha; contraction requires |alpha| < 1. The constant-input hypothesis is separate and is not formally composed with (1).
3. `coherenceStep_norm_mono_of_aligned` — if `C i j = (r : ℂ) * z` with `0 ≤ r ≤ 1`, `0 ≤ α ≤ 1`, `‖z‖ = 1` (`PhaseCoherence.input_norm :95`), then `‖C i j‖ ≤ ‖coherenceStep α C … n i j‖`. This concerns a directed magnitude, not the symmetrised reported R. Proof uses `αr + (1−α) − r = (1−α)(1−r) ≥ 0` and `‖(t : ℂ)‖ = |t|` via `Complex.norm_mul_self_eq_normSq`.

## 3. Honest scope (kept in the module docstring)

Exact reals. **Locking is ASSUMED, not derived** from the closed-loop dynamics; this is not a phase-locking proof (O1 remains open). No float64, no Lean/Python equivalence, no claim that locking occurs, no `B` convergence, no `reported` symmetrisation or zero-diagonal result, no statement about `C j i` or later steps. `AUD-RATELAW stays UNEXPLAINED`. The c016 caveat is not weakened.

## 4. Wiring

`phase_lock_coherence.patch` (5 files, `git apply --check` OK): the new module; `AIEFGateCore.lean` gains one import; `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` regenerated 25 → 26 entries; README paragraph; new SPEC §11.9. **The mutation suite is deliberately unchanged** — adding M60 (drop `+ d`) with a proved negation is an owner follow-up, because the full 59-mutant suite was already not runnable to completion in this sandbox (see Cycle 2 `DELTA_AUDIT.md`). `registry/artifacts_current.csv` is excluded; regenerate with `python3 registry/reconciliation/build_current_inventory.py` in a full clone.

## 5. Local verification

- Target module compiled with zero warnings; `#print axioms` for all three theorems returned only `propext`, `Classical.choice`, `Quot.sound`.
- Full project gate: PASS on the tested source (2,301 jobs, zero warnings; 22 files scanned; 742 declarations audited). Cache download was completed separately; gate used `SKIP_CACHE=1` and reused prior project builds. A subsequent comment-only clarification changed the new source bytes and its checksum; the full gate has not been rerun on those final bytes.
- Existing Python suite: 70 passed on the reconstructed tree.
- Removing `+ d` made the original proof fail at two arithmetic obligations. This is a proof-sensitivity test, **not** a proved counterexample, and is not integrated into CI. Full mutation suite not run.
- Patch applies to the Cycle 2 files in a minimal test tree; full-clone inventory/CI checks not run.

## 6. What this cycle does NOT claim

- No phase-locking proof, no O1 result, no closed-loop claim, no float64 equality.
- No claim promoted/demoted, no erratum, no registry row change, no push, no deletion, no history rewrite, no personal data, no secrets.
- The "R can only go up" statement is **one-step and conditional**; it is not a monotonicity theorem for the full trajectory or for `reported` with symmetrisation.

**Compile command:** `cd lean/AIEFGateCore && SKIP_CACHE=1 ./check_lean_gate.sh` (or `lake build AIEFGateCore.PhaseLockCoherence`).

**Deliverables:** `AIEFS_cycle3/` — `ONE_PAGE_NOTE.md`, `DELTA_AUDIT.md`, `phase_lock_coherence.patch`, `files/`, `evidence.json`, `inventory_delta.csv`, axiom/mutant logs, Lean gate logs.
