# v4.1 fail-closed trust-anchor design and regression controls

**Status: UNVERIFIED INPUT — for independent triage only.**

- **Agent / model:** GPT-6
- **Date:** 2026-11-09 (UTC)
- **Repository / reviewed ref:** jacobbrainard84-knightninja/AIEFS, main@eb3933c196ee19e80e1621ae80d89ca72e6d9485
- **Scope:** Remediation design for the v4.1 manifest/certificate/cohort trust boundary, plus an isolated executable regression harness for the proposed guard. No repository source, registry, CI, or frozen run data was modified.
- **v4.1 source:** AIEF_Experiments/aief_modular_platform_v1_analysis_v4/AIEF_1_4_Twindow_sensitivity_analysis_v4_1.py; Git blob df78b01607e6792afe9afc09fcc9b0cb83585ec6.
- **Registry snapshot:** registry/artifacts_current.csv; Git blob 31be448f5343ce434587e5eaf3d7a397cd3af961.
- **S01 manifest:** runs/b57562a8ee77/manifest.json; Git blob 7ae179db4eda4f6eef8a503567adf8324d94e336.
- **Proposed guard/regression source:** SHA-256 144fa95486e9ba5185d22b439052cb3a0503bcc2a5788040ad1c606147138e86 (15,104 bytes).
- **Execution evidence:** SHA-256 4e819caf3c0d9fca3e318dc2334bcd862da360536cd328d7a4399166f3bd32c9 (4,334 bytes).

## Executive finding

Parts 2–4 established that validate_run can accept a caller-authored manifest and certificate, and that a caller can change child data and simply re-pin the new bytes in that manifest. The existing child-file hash comparison is not broken: it rejects a byte change while its expected digest remains unchanged. The missing control is an independent trust anchor for the manifest and certificate that supply those expected digests.

Part 5 turns that observation into a concrete remediation design and regression harness. The design authenticates exact manifest bytes **before parsing them**, checks the certificate against its own external pin, and checks all declared S01 output digests against policy values that are not taken from the run directory. It also binds the exact ordered 40-seed cohort and run identity.

## S01 trust anchors independently re-read on main

The committed S01 manifest's SHA-256 is 7d1b86ab39eed397e2d281faf729ee5c3ac515efc00b2789c2e0013dce0d1e78. That matches ART-2217 at registry/artifacts_current.csv:2474 (blob 31be448f5343ce434587e5eaf3d7a397cd3af961). The manifest's Git blob is 7ae179db4eda4f6eef8a503567adf8324d94e336.

The manifest's declared output hashes are:

| Output label | SHA-256 | Current-inventory row |
|---|---|---|
| branch_npz | 55a419c790d0a46bad2a52488d9de018a539ad3daa3759eee849cebf4df468c2 | ART-1995, line 2252 |
| scalar_csv | e9aa74e68b758b21e64b5757607af3c4bf98e88f616757319cb9e4e6d3a8e378 | ART-1996, line 2253 |
| baseline_seed_results | 47b1627a20be52ee4cf3ad69feeae3fe8d8e008687912c83c2237dfa8e5363ff | ART-2015, line 2272 |
| baseline_certificate | 08314de365196fa369bfa2b0363352cf04bdfb1a957f3ed86847f5d17b9d620f | ART-2016, line 2273 |
| condition_status_csv | 1f6985026c292c15b5fa8cacacbe92600916ab8d43bdbc8df4f9f0a76baa98e8 | ART-2218, line 2475 |

The baseline certificate therefore has a separate current-inventory pin as well as its matching digest in the authenticated manifest. The committed S01 manifest contains the 40 paired seeds, the expected five rho levels, the four branch names, study_name=AIEF_1_4_Twindow_sensitivity, config_hash=b57562a8ee77, and the model/protocol identity. The test script carries the ordered 40 seed values transcribed from that manifest as strings, avoiding JavaScript's loss of precision for 64-bit JSON integers.

validate_run currently does not compare the supplied manifest bytes with ART-2217 or another independent expected digest. _require_hash reads output_hashes[label] from that supplied manifest and compares the child file with it (source lines 284–292). The manifest status/hash checks occur at lines 295–325; the certificate is reduced to status == passed and n_seeds == 40 at lines 326–329; seed identity is checked for count, uniqueness and internal design coverage at lines 350–372; returned input hashes are recorded at lines 404–421. All references are to source blob df78b01607e6792afe9afc09fcc9b0cb83585ec6 on main@eb3933c196ee19e80e1621ae80d89ca72e6d9485.

## Proposed fail-closed boundary

The regression source implements a standalone verify_trusted_run(run_dir, policy) guard. This is a **design prototype, not a repository patch**. The intended integration point is the first operation inside validate_run, before that function opens or parses the supplied manifest.

1. **No policy, no run.** The trusted policy is a required argument/default from reviewed trusted code or a separately signed, independently pinned policy file. None, incomplete hash maps, malformed hashes or a non-40-seed policy fail closed. The policy must never be constructed from the candidate run's own manifest during the same invocation.
2. **Authenticate raw manifest bytes first.** Hash manifest.json as bytes and compare with the trusted S01 manifest digest. Only after the exact digest matches may the function parse JSON. Even whitespace-only reserialization fails for this frozen S01 input.
3. **Bind identity to that policy.** Require exact study_name, config_hash, run-directory identity and ordered paired-seed list. The authenticated manifest's output_hashes mapping must equal the policy mapping exactly.
4. **Check each child against external values.** Compare the four files used directly by v4.1 and the additional baseline seed-results file against the independently held policy digests. Check the certificate digest separately against ART-2016 as well as requiring its value to agree with the trusted manifest mapping.
5. **Keep existing validation.** After the trusted guard succeeds, retain the existing certificate status/40-seed check, scalar row/column/finiteness/range checks, exact rho/branch checks, status-table coverage checks, and NPZ trajectory/topology checks. Do not weaken them or treat a trusted byte hash as a substitute for shape/schema checks.
6. **No implicit trust expansion.** A new run, seed cohort or analysis study requires a separately reviewed trust-policy entry. freezeable=true is not a trust anchor and does not mean oracle_certified. The S01 manifest does not provide a basis for silently asserting modular oracle certification.

Illustrative integration: call verify_trusted_s01_inputs(inputs, TRUSTED_S01_POLICY) as the first operation inside validate_run, then continue with the existing validation unchanged below it. This placement ensures the CLI and run_analysis paths cannot accidentally omit the guard.

The production policy should be immutable (e.g. literal constants / immutable mappings) and located in an independently reviewed trust module or equivalent configuration. The S01 policy in the prototype carries the manifest digest, all five output digests, the independent certificate digest, the exact seed order, study/config identity and run-directory identity. The helper rejects symlinked input files and a symlinked run path.

### Why not use artifacts_current.csv as the only trust root?

registry/README.md:25–32 (blob b3ab739359393aae5d1e02aded5d4c6885981144) distinguishes the frozen artifacts.csv snapshot from artifacts_current.csv, which is a generated current-tree inventory. tools/ci/check_current_inventory.py:9–25 (blob 0471299194219395d8e94b12494cdccc474c192e) regenerates that inventory and compares it with the committed CSV; the inventory itself is explicitly excepted from its own rows. This is valuable repository consistency enforcement, but it is not a signed trust statement for an arbitrary run directory supplied at runtime.

There is an existing pattern for an independent digest anchor: tools/ci/check_artifact_pins.py:31–33 and :69–74 (blob 653bb60e230d728d739b6204652c483fa1e42083) hard-code the expected digest and row count for the frozen registry/artifacts.csv snapshot. The S01 policy should follow the same general pattern: the expected manifest/certificate digests are held outside the candidate data and changed only in a reviewed update. A signed policy is an alternative if the project later introduces signing.

## Regression test results

The isolated harness uses a deterministic synthetic positive fixture. It freezes a separate policy from the pristine fixture bytes, then runs mutations against copies. It is not genuine S01 data.

| Test | Expected | Observed |
|---|---|---|
| Synthetic trusted fixture | Accept | **Accepted** |
| No independent policy supplied | Reject | **Rejected** |
| Child bytes changed, trusted digest unchanged | Reject | **Rejected** |
| Child bytes changed and input manifest re-pinned | Reject | **Rejected at manifest trust anchor** |
| Certificate bytes changed | Reject | **Rejected at child/certificate digest** |
| Certificate bytes changed and input manifest re-pinned | Reject | **Rejected at manifest trust anchor** |
| Alternate 40-seed namespace in reserialized manifest | Reject | **Rejected at manifest trust anchor** |
| Whitespace-only manifest rewrite | Reject | **Rejected at manifest trust anchor** |
| Symlinked child input | Reject | **Rejected** |

The execution transcript is deposited alongside the reproducer. The result demonstrates that the proposed helper's ordering and hash-binding logic behaves as intended against these controls. It does **not** prove integration with the original module, nor that a real S01 run will pass the guard.

## Required next checks before any promotion

1. Independently re-run the deposited script and compare its embedded S01 policy values with runs/b57562a8ee77/manifest.json and the five inventory rows cited above.
2. Implement the guard on a fresh branch from main, not on audit-inbox; keep the original validator checks and the --allow-unaudited-candidate CLI refusal in place.
3. Add the current Parts 2–4 forged cohorts as regression fixtures. Require each to be rejected at the trust boundary before topology/recovery computations start.
4. Run a genuine S01 positive control with the original 28 MB NPZ, scalar CSV, condition-status CSV, baseline seed-results file and 4.3 MB certificate; record actual file hashes and whether the existing validation/analysis functions complete. These binary inputs were not available locally in this part, so this test remains outstanding.
5. Only after independent triage and successful genuine positive/negative controls should the candidate's audit state be reconsidered. Do not describe the modular platform as oracle-certified on the basis of this work.

## Scope and limitations

- The script executes a separate proposed helper against a synthetic trusted positive fixture and seven synthetic mutation/misconfiguration controls. It does not import or modify the repository's v4.1 module.
- No authentic S01 scalar CSV, NPZ, status CSV, certificate or baseline seed-results JSON was executed. The S01 digests were independently re-read from the committed manifest/current inventory; binary hash execution against the authentic 28 MB NPZ and 4.3 MB certificate remains undone.
- No run_analysis, CLI, bundle writer, simulation, Lean, CI or modular-oracle test was executed.
- This guard authenticates the S01 bundle identity. It does not by itself establish scientific correctness, baseline-equivalence truth, modular oracle certification, or full NPZ schema validity for arbitrary future cohorts.
- No changes were made to main, registries, CI, hash-pinned files, TRIAGE, briefing files, other inbox notes or salvage material.

## Deposit record

- Reproducer: audit_inbox/2026-11-09_gpt-6_v4-1_trust-anchor-regression.py (compressed carrier; pass --extract PATH to write the readable source and verify its SHA-256).
- Execution evidence: audit_inbox/2026-11-09_gpt-6_v4-1_trust-anchor-regression-evidence.txt.
- Review: this file.
- All files remain **UNVERIFIED INPUT** pending independent triage by Researcher 001 and Auditor Seat 002. This submission is not an approval, erratum, confirmed finding or promotion request.
