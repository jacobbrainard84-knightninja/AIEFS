# Local Lean gate check — `AIEFGateCore` at P5 `ab18b068`

**RESULT: PASS (7/7 steps).** This is an independent local rebuild, not CI metadata.

## Environment

- `elan` installed from the official installer; pinned toolchain `leanprover/lean4:v4.33.1` (Lean 4.33.1, commit `819816b2e0a3bf405af45ae5c7af2491d8f5bee6`), Lake 5.0.0.
- Mathlib cache obtained with `lake exe cache get` (completed in 49,745 ms); `lake-manifest.json` mathlib rev `0df444a360eaa60ab8c11dca51a86af692955474` matched the script's expected pin.
- Reconstructed minimal tree: `lean/AIEFGateCore/` (all 24 SUMS-listed files from P5), `lean/AIEFProofs/AIEFProofs/` (4 pinned modules + its SUMS file), `tools/ci/check_pinned_restatement.py`. Project and `TMPDIR` on the 25 GB root filesystem (the first attempt failed at step 4 because `/tmp` is a 992 MiB tmpfs).
- Command: `LOG_DIR=<abs> SKIP_CACHE=0 ./check_lean_gate.sh`. Wall time ~1 hour, dominated by a from-source recompile of the project modules on a 2 GiB-memory sandbox.

## Step results (verbatim from `lean_gate_summary.txt`)

| Step | Result |
|---|---|
| 1 toolchain | PASS — `leanprover/lean4:v4.33.1` |
| 2 pins | PASS — mathlib rev matches; `AIEF_LEAN_GATE_SOURCE_SHA256SUMS.txt` verified (24 files) |
| 2b pinned restatement | PASS — 4 pinned modules, 0 errors |
| 3 imports | PASS — all root imports resolve; no orphans |
| 4 cache | PASS — Mathlib cache completed |
| 5 build | PASS — `Build completed successfully (2299 jobs); warnings=0` |
| 6 markers | PASS — `scanned 20 files, hits=0` (no `sorry`, `admit`, `native_decide`, user `axiom`, `unsafe`, `extern`) |
| 7 axioms | PASS — `AUDITED 707 project declarations; allowed: propext Classical.choice Quot.sound` |

## What this does and does not establish

- It reproduces the P5 branch's own reported result (SPEC §11.7: 2,299 jobs, 0 warnings, 707 declarations) **on a different machine**, with a fresh toolchain install and a fresh `.lake/build`.
- The patch delivered in this cycle changes **no Lean source** relative to P5; README and SPEC are documentation and are not in the Lean SUMS file. The three new Lean modules (`HistoryBuffer.lean`, `PhaseIncrement.lean`, `PhaseCoherence.lean`) are byte-identical to the P5 files that were built here. So this PASS transfers to the patch's Lean content.
- It does **not** run the 58-mutant semantic mutation check, does not prove the Lean convention equals the Python one, and does not validate the new Python probes against Lean.
- Logs are in `lean_gate_logs/` (steps 1–6) and `lean_gate_summary.txt` (full summary). Step 7's generated `#print axioms` file was not copied; its verdict is in the summary.
