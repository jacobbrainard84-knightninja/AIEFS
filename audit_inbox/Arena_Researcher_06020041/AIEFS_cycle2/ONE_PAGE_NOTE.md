# c016 `CoherenceMotion.lean` — one-page port note

**File:** `lean/AIEFGateCore/AIEFGateCore/CoherenceMotion.lean` (new, 336 lines)
**Compile command:** from `lean/AIEFGateCore/`: `SKIP_CACHE=1 ./check_lean_gate.sh` (7-step gate; or `lake build AIEFGateCore.CoherenceMotion` for the single module). Toolchain `leanprover/lean4:v4.33.1`, Mathlib rev `0df444a3…`.

## What it is

Port of Researcher 040282 cycle 016 `CoherenceMotion.lean` (deposit on `audit-inbox` @ `0f189d0`, md5 `079a72f3…`), rated **ADOPT WITH NOTES** by Auditor Seat 002 (`audit_inbox/2026-11-11_auditor-seat-002_lean-candidate-reviews/2026-11-11_audit_040282_c012_c016.md`). It proves the one-step bounds on the complex EMA and on reported `R`:

- `|‖C'‖ − α‖C‖| ≤ 1 − α` for `C' = αC + (1−α)z`, `‖z‖ = 1`;
- `|R_{n+1} − R_n| ≤ min(1, 2(1−α))` on the P5 `coherenceTrace`, given `‖C0 i j‖ ≤ 1`.

At engine `α = exp(−0.01/17.5029…) = 0.99942883…`, `2(1−α) = 0.00114…`, so `R` needs ≥ ~875 steps (≈ 8.75 time units) to go 0 → 1. This is the first quantitative statement about `R` along the real step.

## Honest scope (kept verbatim in the module docstring)

The proof is the triangle inequality on an EMA with unit-norm inputs. **It never uses the phases, the delay, `ω` or `B`** — it holds for any unit-norm input sequence. It is a **speed limit, not dynamics**. Node-uniform probes do not exercise `|C_ij|` vs `|C_ji|` symmetrisation; the bound is about exact reals, not float64; it builds on P5 `PhaseCoherence`, whose engine convention is hand-checked, not proved against Python. No phase locking, no closed-loop claim. `AUD-RATELAW stays UNEXPLAINED`.

## Changes from the deposit

Standard Apache header and scope docstring; module docstring moved **after** the import (Lean requires imports first); trailing `#print axioms` lines removed (step 7 of the gate prints them); nine long/whitespace lint issues fixed so `check_lean_gate.sh` step 5 reports 0 warnings; three unused binders renamed with `_`. Statements and proofs are otherwise unchanged. One theorem added: `false_trace_step_abs_le_half`, a proved negation of the halved bound, used as the negative control for mutant **M59**.

## Wiring (included in `c016_port.patch`)

`AIEFGateCore.lean` gains one import; `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` regenerated (24 → 25 entries); `lean_mutation_check.py` gains M59 (`trace_step_abs_le`, `2*(1−α)` → `(1−α)/2`, refuted by `false_trace_step_abs_le_half`); count pins updated to 39 statement + 20 definition = **59** mutants in `test_lean_gate_p4b.py` and `test_lean_gate_p5.py`; README and SPEC §11.6/§11.8 updated. `registry/artifacts_current.csv` is deliberately excluded — regenerate with `python3 registry/reconciliation/build_current_inventory.py` in a full clone after applying.

## Verification and next step

Local results are in `DELTA_AUDIT.md` (full Lean gate PASS 7/7, isolated M59 verification, 70 Python tests; the full 59-mutant suite is a CI/owner step). Nothing was pushed, committed, merged, or claim-promoted.

**Next cycle (the direction note's second rule):** a genuinely new theorem that uses the phases or the delay — candidate: a condition under which `R` can only increase, e.g. phase increments vanish from time `N` ⇒ `coherenceInput` is constant for `n ≥ N + d` (via `Phase.delayed_input_step`), plus the resulting monotone-up / geometric-convergence statement for the EMA.
