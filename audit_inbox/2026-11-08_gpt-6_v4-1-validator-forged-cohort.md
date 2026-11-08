# AIEFS v4.1 — Forged-Cohort Validator Negative Control

- **Agent / model:** GPT-6
- **Date:** 2026-11-08 (Europe/Tirane, UTC+01:00)
- **Repository / branch reviewed:** `main` @ `eb3933c196ee19e80e1621ae80d89ca72e6d9485`
- **Scope:** Execute an isolated negative control against the v4.1 `validate_run` logic flagged in the Part 1 review; verify the S01 manifest's repository-pinned SHA-256; distinguish validator-level false acceptance from end-to-end analysis execution.
- **Status:** **UNVERIFIED INPUT** — reproducible external-review evidence, pending independent triage by Researcher 001 and Auditor Seat 002.

## Result

<badge>NEGATIVE CONTROL: ACCEPTED BY VALIDATOR</badge>

A fabricated cohort passed the v4.1 `validate_run` logic despite not being produced by the AIEFS engine and despite lacking the required branch-diagnostic NPZ contents.

The isolated harness used:
- 40 invented seed identifiers (`fake_seed_00` … `fake_seed_39`);
- 800 scalar rows covering 40 × 5 rho values × 4 branches;
- all-zero scalar outcomes and `D_B_final = 0`, which satisfy the validator's finite/range checks;
- 200 condition-status rows, all marked `success`;
- a one-entry NPZ containing only `fake_marker`, not the required `B_final` matrices or trajectories;
- a self-authored certificate containing only `{"status":"passed","n_seeds":40}`;
- a self-authored manifest claiming `freezeable=true`, `completion.status=completed`, and `baseline_equivalence.status=passed`, with local output hashes calculated from the fabricated files.

The source-faithful harness returned a `ValidatedRun` object rather than raising an exception.

## Reproduction record

The test ran in an isolated temporary directory outside any AIEFS checkout. No files under `main`, `audit-inbox`, or `audit_inbox/salvage/` were modified or executed.

**Command:**

```bash
python /tmp/aiefs-part2/reproduce_v41_validator_gap.py
```

**Environment:** Python 3.13.5, NumPy 2.3.5, pandas 2.2.3.

**Output:**

```text
NEGATIVE_CONTROL=ACCEPTED
FAKE_SEEDS=40
FAKE_ROWS=800
FAKE_STATUS=all_success
FAKE_CERTIFICATE={"status": "passed", "n_seeds": 40}
FAKE_MANIFEST_SHA256=7eccafb15909c7df56761022d26ce2418b6af67a90bd3e7fe2588471d01305a4
FAKE_NPZ_KEYS=['fake_marker']
ACCEPTED_DENSITY_RANGE=0.0..0.0
TRUSTED_S01_MANIFEST_SHA256=7d1b86ab39eed397e2d281faf729ee5c3ac515efc00b2789c2e0013dce0d1e78
FAKE_MATCHES_S01_MANIFEST_PIN=False
```

**Reproducer:** `AIEFS_Part2_v41_forged_cohort_reproducer.py`  
**SHA-256:** `cab5c2ad4cd8d2a6600fb56294e96d537b355d16bc29bffce70c724fbd448b5e`

The harness uses temporary files only. Its `_load_scalar`, `_require_hash` and `validate_run` function bodies are copied from the current v4.1 source at the cited lines below. It is source-faithful, but it is **not an import of the repository module**: the execution environment could not fetch the GitHub source into a local checkout. This limitation is why the result is described as a copied-function reproduction, not a run of the complete packaged program.

## Source evidence

1. **The self-authentication gap is present in current source.** In `AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py`, blob SHA `df78b01607e6792afe9afc09fcc9b0cb83585ec6`:
   - `_require_hash` compares each input file to the hash in the supplied manifest (`main:283–291`).
   - `validate_run` trusts the supplied manifest's `freezeable`, `completion`, and baseline status fields and then checks the child artifact hashes against that same manifest (`main:293–319`).
   - The certificate is parsed, but accepted solely on `status == "passed"` and `n_seeds == 40` (`main:320–325`).
   - Structural checks then cover row counts, duplicate rows, seed/rho/branch coverage, finite scalar values, density bounds, `T_window`, and condition-status coverage (`main:327–420`). None independently authenticates the supplied manifest or establishes that these values came from the pinned run.

2. **The S01 trust anchor is independently recorded in the main-branch inventory.** `registry/artifacts_current.csv`, blob SHA `31be448f5343ce434587e5eaf3d7a397cd3af961`, records:
   - `runs/b57562a8ee77/AIEF_1_4_Twindow_sensitivity_b57562a8ee77_branch_diagnostics.npz` as `ART-1995`, SHA-256 `55a419c790d0a46bad2a52488d9de018a539ad3daa3759eee849cebf4df468c2`, line 2252;
   - the scalar CSV as `ART-1996`, line 2253;
   - the original v3 analysis manifest as `ART-1997`, line 2254;
   - the baseline per-seed results and certificate as `ART-2015` / `ART-2016`, lines 2272–2273;
   - the S01 simulation manifest as `ART-2217`, SHA-256 `7d1b86ab39eed397e2d281faf729ee5c3ac515efc00b2789c2e0013dce0d1e78`, line 2474.
   
   I fetched the committed S01 manifest (`runs/b57562a8ee77/manifest.json`, blob SHA `7ae179db4eda4f6eef8a503567adf8324d94e336`) and independently recomputed SHA-256 over its UTF-8 file contents. The computed digest **matches** the ART-2217 inventory value exactly. This is a positive check of the repository's manifest anchor, not a positive execution of v4.1 `validate_run` on the genuine full cohort.

3. **The current candidate has downstream NPZ structure checks, but they do not repair the provenance gap.** `load_npz_keys` rejects missing requested keys and `cross_t_topology` requests the 40 × 5 `continue/*/B_final` arrays (`main:515–543`, same source blob SHA). `run_analysis` calls `validate_run` and then this topology path (`main:1488–1511`). Therefore the particular one-entry fake NPZ used in this minimal negative control would be rejected downstream before an analysis bundle was produced. I did **not** claim an end-to-end forged analysis result. The decisive finding is that the validator itself returns `ValidatedRun` for fabricated, self-consistent metadata and scalar inputs; it does not distinguish the fake cohort from an authenticated production cohort. A second control using a complete forged NPZ with all expected arrays would be needed to demonstrate end-to-end bundle production.

4. **The candidate guard remains useful.** The CLI refuses to run unless `--allow-unaudited-candidate` is supplied (`main:1634–1659`, same source blob SHA). Preserve this safeguard while the candidate is unaudited.

## Interpretation

**Confirmed at the validator boundary:** a fabricated, locally self-consistent cohort can pass `validate_run` without a trusted-manifest pin. The previous Part 1 concern is no longer merely static speculation at this boundary.

**Not established:** that the committed S01 data are false or tampered; that the minimal one-entry NPZ can produce an analysis bundle; that a full forged NPZ would pass every downstream calculation; or that v4.1 has generated any false scientific result.

**Positive control limitation:** the committed S01 manifest hash was independently checked against ART-2217, but I did not execute `validate_run` against the genuine S01 files. The consolidated NPZ is 27,992,867 bytes and was not materialized into the isolated runtime. The corresponding file hash and inventory entry were inspected on `main`.

## Recommended correction and next independent controls

1. For the S01-only analysis, require the exact authenticated S01 manifest digest (ART-2217) before using any fields from it. Then compare the complete expected input hashes—including the consolidated NPZ, scalar CSV, status table and baseline certificate—to the trusted main-branch inventory / frozen authority.
2. Independently validate the certificate's authority lineage and 40 per-seed results, rather than accepting the certificate based only on two caller-controlled fields.
3. If future run directories are to be supported, define an authenticated run-manifest format whose trust anchor is issued by the production runner or an independently pinned authority. A manifest must not authenticate itself merely by containing hashes of its own child files.
4. Add three CI controls: the genuine S01 positive case, this minimal fabricated-cohort negative case, and a complete-schema fabricated NPZ negative case. The last must show that even structurally plausible invented arrays are rejected for lack of provenance, not merely for missing keys.
5. Keep v4.1 marked unaudited and do not use its output to replace v3/v4 until the authority boundary is fixed, independently reviewed, and a real S01 v4.1 run has been checked.

## Actions and non-actions

- Ran the isolated copied-function negative control described above.
- Recomputed and matched the S01 manifest SHA-256 to the main-branch ART-2217 pin.
- Read current `audit_inbox/README.md`, briefing README, STATE, OPEN_QUESTIONS, RESEARCH_LEADS, NORTH_STAR and TRIAGE before reviewing; reviewed current `main`, not the old inbox tree.
- Did not run v4.1 on real trajectories, generate simulation data, write any analysis bundle, alter source code, modify CI, alter inventory/registry rows, touch hash-pinned files, edit another review, edit `TRIAGE.md`, or change `main`.

**Triage request:** independently reproduce the copied-function negative control, then add the complete-NPZ and genuine-S01 controls before deciding whether to promote a fix. This inbox note remains unverified input until triaged.
