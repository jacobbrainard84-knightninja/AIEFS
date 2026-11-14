# Cycle 1 — delta audit: P5 merge refresh, doc drift, production-delay probes

**Status:** UNVERIFIED INPUT (outside-agent work). No commit, no push, no merge, no claim-status change. Snapshot: `main` `a559e0d30458bb01989ac47225675d6baec518b8`, `research/lean-gate-p5` `ab18b068e1560b7d6d8005f42ed4d22c7097c8c2`, merge base `75f2b7405ec6eeae36bf20a5e88bedd997788d83`, `audit-inbox` `69221804302921302ca1500ed79d5400cc3663ac`.

---

## 1. Goal and scope

Chosen as the highest-leverage cycle because P5 (history buffer, phase increment, coherence EMA) is the prerequisite for c016 `CoherenceMotion` and c015 `ClosedLoopCore`, and because the newest untriaged inbox note identified a concrete production-delay coverage gap. Deliverables: a reviewed merge-refresh patch, corrected P5 documentation, a new Python engine probe file, and an `audit_inbox/` note draft.

**Not in scope:** new Lean theorems, claim promotion, errata, hash-pinned edits, frozen-run changes, pushes, literature review, or the O1 locking problem.

---

## 2. Method (why no full clone)

A full `git clone` into `/tmp` failed (992 MiB tmpfs; repo working tree ~1.6 GB). Instead:

1. GitHub compare API for `75f2b740...main` (3 files) and `75f2b740...research/lean-gate-p5` (11 files); GitHub tree API for `audit-inbox`.
2. Raw file contents at the merge base, `main` and P5 for the three overlapping files; `git merge-file --diff3` for a content-level three-way merge (no rebase, no history rewrite).
3. All P5 Lean project files fetched by hash from `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` and verified.
4. A minimal git repository containing only the 11 changed paths was used to generate a clean `git diff` patch and to run `git apply --check`.
5. Python tests ran against the unmodified `aief_experiment_engine_v1.py` from `main` (sha256 `ca4593fda86a1b0a3d450d68b5ce4bddd08583fdb93deaf17db20dd6b1acdede`).
6. Lean 4.33.1 (`elan`) was installed from the pinned `lean-toolchain`; `check_lean_gate.sh` was run on a reconstructed minimal P5 project tree. First attempt failed at step 4 because `/tmp` was full; retried with the project and `TMPDIR` on the 25 GB root filesystem.

---

## 3. Merge resolution

| File | Resolution |
|---|---|
| `lean/AIEFGateCore/README.md` | `git merge-file` clean. P5's rows kept; main PR #30's two corrections applied: `stepM_eq_gateM_convex` is affine unless `0 ≤ γdt ≤ 1`, and the mutation check has run in CI since PR #27. Then the stale P5 mutant paragraph was rewritten (§4). |
| `research/lean_gate/SPEC_P1_gate_identities.md` | `git merge-file` clean. P5's §11 kept; main PR #30's three corrections applied (§8.5, §9.5, affine note). §11.6 corrected (§4). |
| `registry/artifacts_current.csv` | **Excluded from the patch.** Six conflict markers from overlapping hash rows; a generated inventory must be rebuilt, not merged. Owner must run `python3 registry/reconciliation/build_current_inventory.py` in a full clone after applying. |
| 8 other P5 files | Taken verbatim from P5 (3 new Lean modules, `AIEFGateCore.lean`, SUMS, `lean_mutation_check.py`, `test_lean_gate_p4b.py`, new `test_lean_gate_p5.py`). |
| New file | `research/lean_gate/tests/test_engine_production_delay.py` (§5). |

`git merge-file` produced **0 conflicts** in README and SPEC; final files contain **no conflict markers**.

---

## 4. Documentation drift repaired (verified, not guessed)

| Claim in P5 @ `ab18b068` | Verified reality | Where fixed |
|---|---|---|
| `SPEC_P1_gate_identities.md:1062` "the mutation check is not run in CI" | `.github/workflows/lean.yml:93-99` runs `lean_mutation_check.py` on the required `AIEFGateCore` row since PR #27 | §11.6 rewritten; README sentence states CI wiring |
| `lean/AIEFGateCore/README.md:52` "23 mutants" | On `main`: 36 (M1–M36). On P5: 38 statement + 20 definition = 58 | README paragraph rewritten |
| `README.md:59` "16 definition mutants M37–M52, 9 equivalence controls, one expected survivor" | Importing P5 `lean_mutation_check.py`: `MUTANTS=38`, `DEF_MUTANTS=20`, `EQUIV_CONTROLS=10`, `TYPO_CONTROLS=3`, `STATEMENT_CONTROLS=2`, `KNOWN_SURVIVORS=0` | README paragraph rewritten |
| `README.md:59` "KNOWN_SURVIVORS documents one expected survivor" | SPEC §11.7 N2: the former S1 is killed by `probe_input_asym_omega_value`; list is empty | README paragraph rewritten |

The genuinely open item — no Lean-side statement-hash pin — is retained in §11.6. `AUD-RATELAW stays UNEXPLAINED` is retained.

---

## 5. Production-delay probes (the cycle's substantive addition)

Confirmed gap: `aief_experiment_engine_v1.py:64-65` (`dt=0.01`, `tau=0.5`), `:95` (`delay_steps=50`), `:711` (51 history copies), `:730` (`compute_R` reads `history[0]`), `:831-834` (coupling reads `history[0]`), `:842-844` (append new theta, pop oldest). But `research/lean_gate/tests/test_engine_step_order.py:40` asserts `delay_steps == 1`, so all four existing probes use a two-slot queue. Lean P5 `HistoryBuffer` is general in `D` but is an abstract sequence, not a Python list/aliasing check.

New `research/lean_gate/tests/test_engine_production_delay.py` (3 tests):

1. **Configuration/initialisation:** `delay_steps == 50`, `alpha == FROZEN_ALPHA`, `len(history) == 51`, all slots equal theta, and the copies are independent (aliasing mutant would fail).
2. **Buffer aging:** 51 deliberately non-constant slots; 51 real `advance_state` calls; before each call `history[0] == initial_history[min(n,50)]`; after each call length 51, newest = appended theta, and `coherence_acc` equals a hand-derived EMA recurrence from `history[0]`. At n = 50 the delayed value is the last initial slot; afterwards all slots are live theta.
3. **Oldest-slot coupling:** N = 2 hand-derived state with distinct slot 1 and newest slot; asserts R, B and theta equal closed forms that differ if the engine reads slot 1, reads newest, or reads current theta (c015 F1 mutant).

The directory is already exercised by `.github/workflows/repo-checks.yml` → `analysis-tests` → `pytest research/lean_gate/tests`, so no CI wiring change is needed.

---

## 6. Verification results

| Check | Command / method | Result |
|---|---|---|
| New probes | `pytest -q research/lean_gate/tests/test_engine_production_delay.py` | **3 passed** |
| Regression | new probes + `test_engine_step_order.py` | **7 passed** |
| Known-false negative control | copy of engine with `compute_R` reading `history[1]`, coupling reading current theta, no oldest-slot pop | **2 of 3 new tests FAIL** (1 config test is insensitive by design) — checks reject known-false input |
| Patch applicability | `git apply --check p5_refresh.patch` against clean `main` tree | **OK** (11 files, 2,036 lines, sha256 `63db39910796b363913b7ccf222d90a4da84c20eafd8b6df2cdaff38aa6bf810`) |
| Lean source pins | `sha256sum -c --strict AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` on P5 sources | **24/24 OK** |
| Forbidden markers | grep `sorry\|admit\|native_decide` across all P5 `.lean` files | **0 hits** |
| Pinned restatement | `tools/ci/check_pinned_restatement.py` | **4 modules, 0 errors, PASS** |
| Mutant inventory | import P5 `lean_mutation_check.py` | 38 + 20 = 58; 10 equivalence, 3 typo, 2 statement controls; 0 survivors |
| Three-way merge | `git merge-file` on README / SPEC | **0 conflicts** |
| Conflict markers | grep on final files | **none** |
| Lean gate check | `./check_lean_gate.sh` with Lean 4.33.1 + Mathlib cache, fresh `.lake/build` | **RESULT: PASS (7/7)** — 2,299 jobs, 0 warnings, 20 files / 0 forbidden markers, 707 declarations on `propext`/`Classical.choice`/`Quot.sound`; see `lean_gate_result.md` and `lean_gate_summary.txt` |

**Not run:** the full repo validator suite (`check_current_inventory.py` etc.) against the patched tree — it requires all 3,095 tracked files, which this workspace snapshot does not contain. `registry/artifacts_current.csv` regeneration is an explicit owner follow-up. No CI was triggered (no push).

---

## 7. Limitations and honest boundaries

- The Lean gate check ran on a **reconstructed minimal tree** (GateCore project + pinned `AIEFProofs` modules + `check_pinned_restatement.py`), not on a full clone; see `lean_gate_result.md` for what passed.
- New Python probes pin the **Python** delay contract only. They do not prove Lean `HistoryBuffer` equals the Python list, do not prove float64 phase locking, and do not close O1.
- No Lean theorem was added, no claim status changed, no hash-pinned file edited, no frozen run touched, no push made.
- The 040282 direction note's two rules were applied to this cycle's own output: minimal deliverable (one patch + one test file + one note), and a result that actually uses the delay. The next *new theorem* still must use phases or delay — candidate: a condition under which `R` can only increase.
- Repository timestamps extend to 2026-11-13 while my session clock reports 2026-09-11; all dates above are repository chronology, reported verbatim.

---

## 8. Files in this cycle

`README.md` (index), `DELTA_AUDIT.md` (this file), `lean_gate_result.md`, `audit_inbox/2026-11-13_arena-agent_cycle1-p5-refresh-and-production-delay.md` (inbox note draft), `p5_refresh.patch`, `files/` (11 resulting files), `inventory_delta.csv`, `evidence.json`.

**Cycle stops here.** The next "continue" can take Cycle 1b (port c016 `CoherenceMotion.lean`, one mutant, one-page note, compile command).
