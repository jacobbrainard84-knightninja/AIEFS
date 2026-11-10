# v4.1 provenance mutation tests — manifest re-pinning and certificate binding

**Status: UNVERIFIED INPUT — for independent triage only.**

- **Agent / model:** GPT-6
- **Date:** 2026-11-09 (UTC)
- **Repository / reviewed ref:** jacobbrainard84-knightninja/AIEFS, main@eb3933c196ee19e80e1621ae80d89ca72e6d9485
- **Scope:** focused mutation testing of v4.1 validate_run's provenance and integrity boundary, using isolated synthetic fixtures and copied source functions. No repository source or trusted file was modified.
- **Source file:** AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py; Git blob df78b01607e6792afe9afc09fcc9b0cb83585ec6 on the reviewed main commit.
- **Reproducer source SHA-256:** 504d8240518165e142f553f29b01dbe307d22b1528b21af5c6f87c23ed9d42ea (16,413 bytes).
- **Execution evidence SHA-256:** 42e373c13cc7deb907559d124acbf1ec74d9c0f5154e4901ac4a8f31e4d7d981 (1,967 bytes).

## Result

This part isolates an important distinction: v4.1 does enforce the child-file hash values supplied by the manifest, but it does not authenticate that manifest or its claimed provenance against the committed S01 trust anchors.

### Executed mutation matrix

| Test | Expected behavior | Observed |
|---|---|---|
| Caller-supplied fabricated manifest and certificate; 40 invented seed IDs | Reject absent external authentication | **ACCEPTED** |
| Change scalar CSV bytes, leave its original manifest digest unchanged | Reject | **REJECTED** |
| Make the same scalar CSV byte change, update output_hashes.scalar_csv in the supplied manifest | Reject untrusted re-pinning | **ACCEPTED** |
| Add contradictory provenance-shaped fields to the synthetic certificate, rehash that certificate in the supplied manifest | Reject contradiction | **ACCEPTED** |
| Set certificate status to failed, update its digest | Reject | **REJECTED** |
| Set certificate n_seeds to 39, update its digest | Reject | **REJECTED** |
| Replace the fake seed namespace with another 40 distinct identifiers and matching scalar/status rows | Reject non-S01 cohort | **ACCEPTED** |

The script reports four accepted forged/provenance scenarios and three correctly rejected local integrity/status controls. Exact console output, including exception text and the synthetic manifest digest, is in the deposited evidence transcript.

### What the validator does enforce

- It requires the five input paths to exist.
- It requires manifest flags for freezeable, completed and baseline-equivalence status.
- It checks each child file's bytes against the expected digest stored in that same manifest.
- It checks the baseline certificate's status equals passed and n_seeds equals 40.
- It requires 800 scalar rows with specified fields, no duplicate seed/rho/branch tuples, finite scalar outcomes, valid density range, expected rho levels and branch order, and a consistent T_window.
- It requires 200 success status rows covering the seed/rho pairs named in the manifest.

The mutation control demonstrates that the child-file hash check is useful: changing the scalar CSV without changing the manifest digest is rejected at _require_hash. The problem is not the existence of that check; it is the absence of an independently trusted root for the manifest supplying the expected digests.

### What the mutation tests show is not authenticated

1. **Manifest identity is not tied to the pinned S01 manifest.** The fabricated manifest had SHA-256 93a89fb0e6e381d10355b857b33aba6be84614ac850daa2454820eb7b4f12404, not the committed S01 ART-2217 digest, yet validate_run accepted it. The validator also accepted a second caller-authored manifest after its child digest was updated to match changed bytes. No trusted manifest digest is compared before those child hashes are consumed.

2. **Certificate provenance is not bound.** The synthetic certificate included status=passed and n_seeds=40, but also deliberately contradictory extra fields: n_seeds_tested=1, n_seeds_passed=0, a false frozen_input_hashes mapping, a false engine_source_sha256 and a false frozen_manifest_hash. After updating the supplied manifest's certificate digest to match this changed certificate, validate_run accepted it. The certificate's status and n_seeds fields remain real checks: the separate status=failed and n_seeds=39 negative controls were rejected.

3. **Seed identifiers are not anchored to S01.** The validator requires 40 distinct seed strings, and checks scalar/status coverage against those strings. It does not compare them with the ordered paired_seeds list in the independently committed S01 manifest. A second synthetic cohort using alternate_fake_00 through alternate_fake_39, with matching scalar and status tables, was accepted.

4. **Several identity metadata fields are optional to validate_run.** A minimal synthetic manifest was accepted without run_id, study_name, spec_sha256, config_hash, source_sha256, schema, or signed identity metadata. It also omitted oracle_certified. This does not by itself establish that every omitted field must be required for an analysis-only reanalysis. It does establish that validate_run does not prove those identities or oracle certification. freezeable must not be described as oracle_certified.

5. **The manifest's calculated hash is only recorded, not independently checked.** The returned ValidatedRun input_hashes include the supplied manifest's byte hash at source lines 404–410. That is useful provenance bookkeeping after acceptance, but it does not authenticate the manifest because no independently trusted digest is compared at that point.

## Exact source references

All references below are to source blob df78b01607e6792afe9afc09fcc9b0cb83585ec6 on main@eb3933c196ee19e80e1621ae80d89ca72e6d9485.

- _require_hash, lines 284–292: reads manifest.output_hashes[label], hashes the local file, and compares those values.
- validate_run manifest status gates, lines 295–316: checks presence, object shape, freezeable, completion.status and baseline_equivalence.status.
- Supplied-manifest child hash loop, lines 318–325.
- Baseline certificate check, lines 326–329: only status and n_seeds are checked.
- Scalar table required fields / row count / duplicate conditions, lines 331–349.
- Paired seeds, rho values, branches and internally consistent condition coverage, lines 350–372.
- Scalar finite/range and T_window checks, lines 374–389.
- Condition-status row count, success values and internal coverage, lines 390–398.
- B_c check and returned input_hash bookkeeping, lines 400–421.

Independent S01 anchors on the same main commit:

- registry/artifacts_current.csv, Git blob 31be448f5343ce434587e5eaf3d7a397cd3af961, line 2474: ART-2217 pins runs/b57562a8ee77/manifest.json to SHA-256 7d1b86ab39eed397e2d281faf729ee5c3ac515efc00b2789c2e0013dce0d1e78.
- The committed S01 manifest is runs/b57562a8ee77/manifest.json, Git blob 7ae179db4eda4f6eef8a503567adf8324d94e336. Its file SHA-256 matches ART-2217.
- registry/artifacts_current.csv, same blob, line 2273: ART-2016 pins runs/b57562a8ee77/baseline_equivalence_certificate.json to SHA-256 08314de365196fa369bfa2b0363352cf04bdfb1a957f3ed86847f5d17b9d620f.
- The S01 consolidated branch NPZ is independently pinned as ART-1995 at line 2252. The full-schema fake NPZ acceptance was separately exercised and reported in the Part 3 note.

## Recommendations for independent triage

1. **Authenticate the expected run before checking child files.** For this S01-specific candidate, compare the supplied manifest bytes with ART-2217 (or with a separately established trusted allow-list/pin record) before consuming manifest.output_hashes. For a generalized tool, pass the trusted manifest digest or trusted run identity as a separately sourced input; do not let the input manifest provide its own trust root.

2. **Authenticate the baseline certificate independently.** For the pinned S01 run, verify the certificate bytes against ART-2016 before reading it. Then validate certificate identity and claims against the authenticated run: frozen input digests, source/engine identity, seed count and passed/tested counts. A status/count pair must not stand in for certificate provenance.

3. **Bind the cohort to the authenticated manifest.** Compare the ordered paired seed list, study identity, rho grid, branch set, model constants, T_star and run/spec identity with the committed S01 manifest, rather than only checking that 40 arbitrary seed strings form a self-consistent design.

4. **Keep the child-hash check.** It correctly rejects byte changes when its expected hash is stable. Add a negative control where the attacker changes an artifact and updates its digest in an untrusted manifest; require rejection because the manifest itself is not authenticated.

5. **Specify oracle-certification policy separately.** The candidate's freezeable S01 requirement and the project's oracle-certification status are different notions. Do not infer oracle certification from freezeable. If oracle certification is a prerequisite for a downstream scientific claim, enforce it as a separately named, independently sourced gate; otherwise label the reanalysis scope accurately.

6. **Retain the Part 3 complete-schema forged-cohort fixture.** Part 4 tests provenance binding only. Part 3 demonstrated that a forged NPZ with the full key and shape contract can reach the copied downstream calculations. Both tests should remain distinct regression cases.

## Scope limits

- The harness contains copied source bodies for _load_scalar, _require_hash and validate_run, corresponding to source lines 274–421. It is a source-faithful isolated reproduction, not an import of the complete repository module.
- All files and identifiers in the mutation cases are synthetic. No genuine S01 scalar CSV, NPZ or baseline certificate was executed.
- No full run_analysis, CLI, bundle writer, module dependency imports, CI, Lean or simulation execution occurred.
- The baseline certificate mutation uses extra contradictory test fields to demonstrate that validate_run ignores fields other than status and n_seeds; it is not a claim that this synthetic certificate is the complete production certificate schema.
- No source, registry, CI, Triage, briefing, frozen file, other inbox note or salvage file was changed.

## Deposit record

- Reproducer: audit_inbox/2026-11-09_gpt-6_v4-1_provenance-mutation-reproducer.py.
- Execution transcript: audit_inbox/2026-11-09_gpt-6_v4-1_provenance-mutation-evidence.txt.
- Review: this file.
- All deposits remain UNVERIFIED INPUT until independently triaged by Researcher 001 and Auditor Seat 002. This is not an approval, confirmed finding, erratum or promotion request.
