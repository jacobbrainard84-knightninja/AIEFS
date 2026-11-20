# v4.1 P1 input-trust gap: independent reproduction on the real module and genuine S01 data

- Author: Auditor Seat 002, 2026-11-09 (Europe/Tirane)
- Reviewed ref: `main @ eb3933c196ee19e80e1621ae80d89ca72e6d9485` (fresh detached worktree)
- Source under test: `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py`, sha256 `119f679ca8c45f61a27ca907791bc8cf3dcd93677f336b565c130ec36bbb2baa`
- Inputs: the committed S01 run `runs/b57562a8ee77/` (manifest sha256 `7d1b86ab…1e78` = ART-2217)
- Script: `p1_control.py` (this folder; sha256 `6351847ec231fd038e5a5c9f4c2041166b0f6fce58399ed137680c53974f3171`). Written by Auditor Seat 002. No GPT-6 script was executed.
- Run: `PYTHONPATH=<repo>/AIEF_Experiments/aief_modular_platform_v1_analysis_v4 python3 -B p1_control.py` (Python 3.13.5, numpy 2.5.4, pandas 3.0.6). Output: `p1_evidence.txt`.

## Result: GPT6-P1 REPRODUCED

This imports the real `validate_run` and `discover_inputs` from the module on main. It does not use copied functions. Every mutated run is a copy in a temp dir, and the committed files were not changed.

| Case | Expected after a fix | Observed on main |
|---|---|---|
| POS: genuine S01 run dir | accept | ACCEPTED (40 seeds, 800 rows) |
| N1: one `D_B_final` value edited, manifest untouched | reject | REJECTED (scalar_csv hash mismatch) |
| N2: same edit, `output_hashes.scalar_csv` re-pinned in manifest | reject | **ACCEPTED** |
| N3: certificate replaced by `{"status":"passed","n_seeds":40}`, re-pinned | reject | **ACCEPTED** |
| N4: all 40 seeds renamed consistently (manifest, scalar CSV, status CSV), re-pinned | reject | **ACCEPTED** |

The forged manifest in N2 does not match the ART-2217 pin, and nothing in `validate_run` checks for that. The child-file hash check works (N1), but it only compares files against the manifest it was handed. Anyone who edits data and re-pins the manifest gets through.

This is the first **genuine positive control**: the real 28 MB NPZ, scalar CSV, status CSV and 4.3 MB certificate all pass the current validator, and their on-disk digests match the five values in GPT-6's trust-anchor note (branch_npz 55a419c7…, scalar_csv e9aa74e6…, baseline_certificate 08314de3…, manifest 7d1b86ab…). GPT-6 could not run this step.

Scope limits: this tests `validate_run` only. It does not run `run_analysis`, the CLI or the bundle writer, and the `--allow-unaudited-candidate` guard was not bypassed. v4.1 is still a candidate that nobody has audited. Nothing here is a scientific result.

## Direction

- Fix on a normal branch from main (v4.1 is not hash-pinned): add a guard at the very top of `validate_run` that hashes the raw manifest bytes against a hard-coded S01 policy before parsing. Then check the five output digests and the certificate digest against that same policy, and bind the exact ordered seed list and study/config identity. Keep every existing check. Use N2–N4 as rejecting tests and POS as the positive test. Dual control: whoever authors it does not approve it.
- GPT-6's trust-anchor design note is a reasonable outline. Its policy values agree with the committed files for the digests checked above. Its prototype was not executed by this seat.

## Correction to my PR #16 review side-note (`2026-11-09_auditor-seat-002_chronicler-corrigenda-review.md`)

The ControllerFiber "hash drift" is not a broken pin. `lean/AIEFProofs/AIEFProofs/ControllerFiber.lean` changed once after registration: the snapshot was `d2f8452` (sha256 `37c26f56…`, ART-0745 in `registry/artifacts.csv`), and the current bytes come from `d041c69` (sha256 `b51e07e8…`). The diff is header-only. The copyright holder line changed and an `SPDX-License-Identifier: Apache-2.0` line was added, with no theorem or proof text touched. The current hash matches `AIEF_LEAN_SOURCE_SHA256SUMS.txt`, `audit_manifest.json`, `lean_r4/source_sha256.txt`, and the `KNOWN_CHANGED` entry in `tools/ci/check_artifact_pins.py`. The only gap is wording: ERRATA E7 names ART-0744 and ART-0746 but not ART-0745. That is an optional one-line clarification, not an urgent erratum.
