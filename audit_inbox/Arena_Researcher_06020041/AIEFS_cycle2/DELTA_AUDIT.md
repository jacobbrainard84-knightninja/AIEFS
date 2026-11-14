# Cycle 2 — delta audit: port of c016 `CoherenceMotion.lean`

**Status:** UNVERIFIED INPUT (outside-agent work). No commit, no push, no merge, no claim-status change. Base: the Cycle-1-refreshed patch (`p5_refresh.patch`, sha256 `63db3991…`) applied conceptually to `main` `a559e0d30458bb01989ac47225675d6baec518b8`; P5 `ab18b068…`; `audit-inbox` `69221804…`; c016 deposit at `audit-inbox` `0f189d0`.

---

## 1. Goal

Highest-leverage next item after the P5 refresh: land the small, already-reviewed c016 coherence-motion result as a proper `AIEFGateCore` module, wire one semantic mutant, and verify it locally. Per the 040282 direction note: minimal deliverable (one `.lean`, one-page note, compile command) and no giant bundle. The directive's second rule (the *next new theorem* must use phases or delay) is explicitly scheduled for Cycle 3; this cycle is a port, not a new result.

## 2. Method

- Reinstalled `elan` and Lean 4.33.1 (installed packages do not persist across sessions), fetched the Mathlib cache (8,690 files), and reconstructed the P5 `AIEFGateCore` project from the 24 SUMS-listed files plus the pinned `AIEFProofs` modules and `check_pinned_restatement.py`.
- Ported the c016 deposit with format-only changes (§3), added it to the root import and regenerated `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` (25 entries).
- Ran `check_lean_gate.sh` (fresh `.lake/build`, `REUSE_BUILD=1` after a targeted module build), the full Python test suite, and an isolated M59 verification using the project's own `lean_mutation_check.py` machinery.

## 3. The port

`lean/AIEFGateCore/AIEFGateCore/CoherenceMotion.lean` (328 lines). Statements and proofs of the deposit unchanged. Differences: standard Apache/SPDX header; scope docstring (including the auditor's "speed limit, not dynamics" limitation); module docstring moved **after** the `import` (the first compile failed at line 30 with "invalid 'import' command"); 21 trailing `#print axioms` lines removed; nine long-line/whitespace lint issues and three unused binder names fixed to reach **0 warnings**; one theorem added, `false_trace_step_abs_le_half` (negative control for M59).

What it proves: one-step complex-EMA / reported-`R` movement bounds on P5's `coherenceTrace`, including `|R_{n+1} − R_n| ≤ min(1, 2(1−α))` for `0 ≤ α ≤ 1`, `∀ i j, ‖C0 i j‖ ≤ 1`. Engine `α = exp(−0.01/17.5029…) = 0.99942883…` ⇒ `2(1−α) = 0.00114…` per step, ≥ ~875 steps (≈ 8.75 time units) for 0 → 1.

**Scope kept verbatim:** triangle inequality on an EMA with unit-norm inputs; uses no phases, delay, `ω` or `B`; not float64, not Lean/Python equivalence, not phase locking, not closed-loop. `AUD-RATELAW stays UNEXPLAINED`.

## 4. Wiring in `c016_port.patch` (8 files, 534 lines, `git apply --check` OK)

| File | Change |
|---|---|
| `AIEFGateCore.lean` | `+ import AIEFGateCore.CoherenceMotion` |
| `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` | regenerated, 24 → 25 entries |
| `CoherenceMotion.lean` | **new** |
| `lean/AIEFGateCore/README.md` | counts 39 statement + 20 definition = 59; M59 description; honest note on the un-run full suite |
| `research/lean_gate/SPEC_P1_gate_identities.md` | §11.6 updated, new §11.8 (c016 port, M59, results) |
| `research/lean_gate/lean_mutation_check.py` | M59 entry + docstring; `OPENS` gains `open AIEFGate.CoherenceMotion (rTrace)` (needed because the generated refutation file lives in namespace `AIEFGate`) |
| `tests/test_lean_gate_p4b.py` | pin `len(names) == 39`, M59 slice assertions |
| `tests/test_lean_gate_p5.py` | `N_STATEMENT_MUTANTS = 39`, `TOTAL_MUTANTS = 59`, docstring |

`registry/artifacts_current.csv` is again excluded (generated inventory; regenerate with `python3 registry/reconciliation/build_current_inventory.py` in a full clone).

## 5. Verification results

| Check | Result |
|---|---|
| `./check_lean_gate.sh` (Lean 4.33.1 + Mathlib cache, fresh build) | **PASS 7/7** — step 5: `Build completed successfully (2300 jobs); warnings=0`; step 6: `scanned 21 files, hits=0`; step 7: `AUDITED 739 project declarations; allowed: propext Classical.choice Quot.sound`. Step 2: 25/25 SUMS; step 2b: 4 pinned modules PASS; step 3: all imports resolve. |
| `sha256sum -c --strict AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` | 25/25 OK |
| `lake env lean AIEFGateCore/CoherenceMotion.lean` | 0 warnings, 0 errors |
| `pytest research/lean_gate/tests` | **70 passed** (includes the Cycle-1 production-delay probes and the updated 39/59 count pins) |
| Isolated M59 verification (harness `lean()` machinery) | **PASS** — (a) mutated `trace_step_abs_le` fails to build with a `REAL PROOF FAILURE`; (b) `CoherenceMotion.false_trace_step_abs_le_half H` elaborates as `¬ prop` with `#print axioms` = `[propext, Classical.choice, Quot.sound]`; (c) the same term fails on the unmutated statement (term-specificity). Log: `verify_m59.log`. |
| `git apply --check c016_port.patch` | OK |
| PII scan of markdown deliverables | no matches |

**Not completed:** the full 59-mutant suite. Each `lake env lean` invocation reloads the ~2,300-module Mathlib import graph (~2 min per call in this 2 GiB sandbox); a 49-minute run was stopped before completion. This is **not** claimed as a pass. It remains a CI/owner step — `.github/workflows/lean.yml` runs `lean_mutation_check.py` on the required `AIEFGateCore` row. M59 itself is verified in isolation with the harness's own build/refutation/specificity checks.

## 6. Limitations and honest boundaries

- The gate check ran on a reconstructed minimal tree (GateCore + pinned AIEFProofs + the checker), not a full clone; the patch changes no other Lean source, so the result transfers.
- No proof that the Lean convention equals the Python one; no float64 phase-locking result; no closed-loop claim; no new phase/delay-dependent theorem.
- No claim promoted/demoted, no erratum, no registry row change, no hash-pinned or frozen file edited, no push, no deletion, no history rewrite.
- Installed toolchain and Mathlib cache do not persist across sessions; each Lean cycle requires a reinstall and a from-source project rebuild (~45 min here). This is an environment limitation, not a repo defect.
- Repository timestamps extend to 2026-11-13 while the session clock reports 2026-09-11; all dates above are repository chronology.

## 7. Next cycle

The direction note's second rule: a genuinely new theorem that **uses the phases or the delay**. Concrete candidate: `input_constant_after_lock` — if phase increments `u n = 0` for `n ≥ N`, then `Phase.delayed_input_step` plus `delayedIncrement` give `coherenceInput (n+1) = coherenceInput n` for `n ≥ N + d`; then EMA error contracts geometrically (`‖C_{n+k} − z‖ = α^k ‖C_n − z‖`) and, when `C_n` is aligned with `z` and `‖C_n‖ ≤ 1`, reported `R` is non-decreasing. All hypotheses must be explicit; no locking or closed-loop claim. One `.lean`, one-page note, compile command, one mutant.

**Cycle stops here.**
