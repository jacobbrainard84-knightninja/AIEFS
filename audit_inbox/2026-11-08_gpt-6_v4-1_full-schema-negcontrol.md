# v4.1 complete-schema forged-cohort negative control

**Status: UNVERIFIED INPUT — for independent triage only.**

- **Agent / model:** GPT-6
- **Date:** 2026-11-08 (UTC)
- **Repository / reviewed ref:** \`jacobbrainard84-knightninja/AIEFS\`, \`main@eb3933c196ee19e80e1621ae80d89ca72e6d9485\`
- **Scope:** v4.1 candidate input trust boundary; isolated synthetic complete-schema cohort; copied v4.1 validation, downstream topology/recovery, interaction, and summary calculations. No source, registry, CI, CLI, or bundle-writer changes.
- **Source file:** \`AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py\`, Git blob \`df78b01607e6792afe9afc09fcc9b0cb83585ec6\` on reviewed \`main\`.
- **Reproducer:** \`audit_inbox/2026-11-08_gpt-6_v4-1_full-schema-reproducer.py\`; launcher SHA-256 \`bbd6dba50d9976e01c915853f41afabc70200f8c046b9e86153d6b547d99f2f6\` (16,978 bytes). The launcher expands a readable standalone harness whose SHA-256 is \`824ce4f7e45752d092faed4740edef141f4c4a01ac3526be1f33db8e125e9201\` (46,517 bytes; 861 lines). Run \`python <script> --extract <path>\` to inspect the expanded source, or run it without arguments to execute.

## Result

The prior validator-only negative control was strengthened. The new isolated test builds an invented 40-seed cohort with 800 scalar rows, 200 successful condition-status rows, a minimal self-consistent \`baseline_equivalence_certificate.json\`, a caller-authored manifest whose \`output_hashes\` match the generated files, and a compressed NPZ containing every array that the v4.1 raw analysis calculations consume:

- 2,400 trajectory arrays: 40 seeds × 5 rho values × 4 branches × (\`sample_times\`, \`density_trajectory\`, \`similarity_trajectory\`)
- 200 \`continue\`-branch \`B_final\` matrices, each 12×12
- 2,600 total NPZ keys

All data are fabricated. Seed identifiers are \`fake_seed_00\` through \`fake_seed_39\`. The matrices have uniform 0.5 off-diagonal weights; the 640-point saved-grid trajectories are uniform 0.99. Scalar outcomes are simple deterministic synthetic values; they are not produced by the engine or by the S01 study.

**The copied \`validate_run\` accepted the forged cohort.** More importantly, the forged NPZ did not fail at the downstream array consumers: the source-copied topology, recovery-event, AUC, interaction and summary calculations all completed and met the exact hard-coded row-count checks used in \`run_analysis\`.

Executed output (Python 3.13.5, NumPy 2.3.5, pandas 2.2.3; command: \`python AIEFS_Part3_v41_full_schema_reproducer.py\`):

\`\`\`text
NEGATIVE_CONTROL=ACCEPTED_BY_VALIDATE_RUN
FAKE_SEEDS=40
FAKE_SCALAR_ROWS=800
NPZ_TOTAL_KEYS=2600
EXPECTED_TRAJECTORY_KEYS=2400
EXPECTED_CONTINUE_BFINAL_KEYS=200
NPZ_KEYS_COMPLETE=True
REGIME_CONTRAST_ROWS=960
BRANCH_INTERACTION_ROWS=2880
CROSS_T_TOPOLOGY_ROWS=160
CROSS_T_TOPOLOGY_ALL_FINITE=True
CROSS_T_TOPOLOGY_UNIQUE_VALUES=[{'cross_T_cosine': 0.9999999999999998, 'cross_T_Jaccard': 1.0, 'cross_T_normalized_distance': 0.0}]
RECOVERY_EVENT_ROWS=19200
RECOVERY_AUC_ROWS=1600
RECOVERY_FIRST_CROSSING_ALL_OBSERVED=True
RECOVERY_SUSTAINED_ALL_OBSERVED=True
RECOVERY_HELD_RECOVERY_NONE_AS_EXPECTED=True
RECOVERY_EVENT_TIMES_UNIQUE=[0.01]
RECOVERY_AUC_UNIQUE=[0.0]
RECOVERY_EVENT_DID_ROWS=11520
RECOVERY_AUC_DID_ROWS=960
SUMMARY_COUNTS={'regime': 24, 'branch_DID': 72, 'topology': 12, 'recovery_event': 2400, 'recovery_AUC': 80, 'recovery_event_DID': 1440, 'recovery_AUC_DID': 24}
SUMMARY_COUNTS_MATCH_RUN_ANALYSIS=True
RUN_ANALYSIS_RAW_COUNTS_MATCH_SOURCE=True
FAKE_MANIFEST_SHA256=3a9057101ed087224ba99f8dac8f218f94382ca91e92e63b929515f3a3381c32
FAKE_MANIFEST_MATCHES_TRUSTED_S01_PIN=False
FAKE_NPZ_SHA256=1559bee026e59468405b6e84bbdffd54a22d9a25f32afe87e633914578896af6
FAKE_NPZ_BYTES=1603862
NOTE=Copied source functions executed in isolation; no full CLI, bundle writer, or genuine S01 artifacts executed.
\`\`\`

The zero AUC and topology values are not evidence of a real effect: they are direct consequences of the deliberately uniform synthetic arrays. The \`held_recovery\` events are correctly unobserved because the fabricated series never drops below its recovery threshold; the first-crossing and sustained-through-last-observation rows are observed at the first saved sample, 0.01.

## Source-grounded trust-boundary observations

1. **The manifest is not authenticated to the committed S01 authority.** \`_require_hash\` (\`:284–292\`) compares each child file with the digest asserted in the *supplied* manifest. \`validate_run\` (\`:295–325\`) checks a few status fields and then applies those same-manifest hashes. It does not compare the manifest's own bytes with an external trust anchor or the committed S01 pin. The fake manifest's hash is \`3a905710…\`, and it does not match the committed S01 manifest pin. It was nevertheless accepted.
2. **The baseline certificate check is only a status/count check.** \`validate_run\` opens the certificate and requires \`status == "passed"\` and \`n_seeds == 40\` (\`:326–329\`). The test's newly fabricated two-field certificate passed; the validator does not authenticate certificate identity or its frozen-input/source provenance against a trusted authority.
3. **Cohort identity is caller-controlled.** The validator checks 40 distinct seed strings and coverage against those strings (\`:350–372\`), but does not require them to match the committed S01 paired seed list. The 40 invented \`fake_seed_*\` identifiers passed.
4. **The validator does not inspect the NPZ.** \`validate_run\` checks that the file exists and its hash matches the caller's manifest, then returns (\`:318–324\`, \`:404–421\`). NPZ keys are first opened downstream by \`load_npz_keys\` (\`:519–535\`). The forged archive contained exactly the downstream-consumed keys, so \`cross_t_topology\` (\`:538–560\`) and \`compute_recovery\` (\`:738–891\`) both ran.
5. **The downstream analysis checks are not a provenance check.** They validate matrix shape/finiteness, saved-grid schedule, trajectory shapes/ranges, and derived metric finiteness. They cannot tell that a coherent set of arrays and scalar rows was invented when the manifest and certificate are also fabricated.

The committed S01 manifest is \`runs/b57562a8ee77/manifest.json\`, Git blob \`7ae179db4eda4f6eef8a503567adf8324d94e336\`. Its SHA-256 matches the ART-2217 entry in \`registry/artifacts_current.csv\` (\`:2474\`), blob \`31be448f5343ce434587e5eaf3d7a397cd3af961\`: \`7d1b86ab39eed397e2d281faf729ee5c3ac515efc00b2789c2e0013dce0d1e78\`. The actual S01 manifest's \`schema\` object begins at \`:202\`, with \`required_branch_matrix_keys\` and \`required_branch_scalar_keys\` beginning at \`:282\` and \`:305\`. The validator does not compare these schema declarations or the manifest's own hash with an external pin. The Part 3 forged archive provides the minimal key set needed by the current v4.1 downstream calculations.

The manifest/inventory also identify the genuine S01 consolidated NPZ as a 27,992,867-byte binary file, SHA-256 \`55a419c790d0a46bad2a52488d9de018a539ad3daa3759eee849cebf4df468c2\` (ART-1995; inventory blob above). Its hash agrees with the genuine S01 manifest's \`output_hashes.branch_npz\`. This is a metadata cross-check only: the binary NPZ could not be retrieved through the text-only GitHub file interface, so **no genuine S01 \`validate_run\` positive execution was performed**.

## Scope limits

- This was an isolated, source-faithful copied-function harness, not an import of the complete repository module. The validator body came from \`:274–421\`; downstream functions were copied from the cited source blob and invoked against the temporary fake cohort.
- The raw analysis tables, DID calculations, and summary calculations were exercised, including all \`run_analysis\` raw-row and summary-row count checks. \`run_analysis\` itself, \`build_report\`, \`_write_bundle\`, the CLI, and the actual S01 inputs were **not** executed. Do not claim an analysis bundle was created.
- The candidate source itself says it is unaudited and “DO NOT RUN ON REAL TRAJECTORIES” (\`:2–10\`); \`main()\` also requires the explicit \`--allow-unaudited-candidate\` opt-in (\`:1634–1659\`). Neither guard was bypassed, and no genuine trajectories were used.
- No simulation, Lean, CI, modular-oracle, or study-registry work was performed in this part.

## Recommendations for independent triage

1. Make the committed S01 manifest (or an independently trusted registry/pin record) the trust anchor. Require the supplied manifest's SHA-256 to match that trust anchor before using any of its child-file hashes. Do not let an untrusted manifest authenticate itself.
2. Bind the baseline-equivalence certificate to the same trusted run identity: compare its frozen input hashes, engine/source hash, seed count and relevant cohort metadata with the independently authenticated source records, rather than accepting only \`status\` and \`n_seeds\`.
3. Require the exact authenticated paired-seed list and expected study/protocol/model identity, not just any 40 distinct strings and an internally consistent 800-row design.
4. Add a checked schema contract for the arrays actually needed by v4.1 (the 200 \`continue/B_final\` matrices and 2,400 trajectory arrays), and make the intended minimum-vs-full S01 schema explicit. Keep trajectory/matrix dimension and finiteness checks. Add a negative fixture identical in spirit to this complete-schema forgery and require rejection before analysis.
5. Add a genuine S01 positive-control test after the trust-root fix, using the committed S01 files and exact pinned hashes; preserve the \`--allow-unaudited-candidate\` guard until independent audit is complete.

**Disposition requested:** Researcher 001 / Auditor Seat 002 should independently rerun the deposited reproducer, verify the copied source against \`main@eb3933c…\`, assess whether the candidate's minimal analysis-input schema is intentional, and record triage. This submission is not an approval, erratum, or promotion request.

## Deposit record

- Supporting reproducer: \`audit_inbox/2026-11-08_gpt-6_v4-1_full-schema-reproducer.py\` (launcher SHA-256 above; embedded expanded source SHA-256 above).
- Review: this file.
- Both files are to remain **UNVERIFIED INPUT** until independent triage.
- No edits were made to \`main\`, existing inbox files, TRIAGE, briefing documents, registries, hash-pinned files, or salvage material.
