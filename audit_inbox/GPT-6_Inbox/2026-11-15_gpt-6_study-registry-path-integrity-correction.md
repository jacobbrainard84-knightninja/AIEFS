# GPT-6 outside-audit review — study registry path integrity (corrected full submission)

> **UNVERIFIED INPUT — corrective full submission.** This is the substantive review for triage. The same-topic path without the suffix “-correction” is an empty placeholder accidentally created at commit 47cb2da86619143c6c62dec566cb6a0522265a17 (zero-byte blob e69de29bb2d1d6434b8b29ae775ad8c2e48c5391). The audit-inbox rules are add-only, so that placeholder is intentionally left untouched. Please triage this correction file and ignore the zero-byte placeholder. This report is not a finding, claim, erratum, registry correction, approval, or instruction to integrate.

- **Agent / model:** GPT-6
- **Date:** 2026-11-15 (Europe/Tirane)
- **Main reviewed:** 871417d58504dd2e42276bde8142e3fdac73df44
- **Main tree:** 31b4959951ac47846a2abee5fac6ed02e1350fa3
- **Audit-inbox context read at:** 0af70440ee8f66195e6da73439307d3869884fe1
- **Scope:** Re-check all registry/studies.csv canonical entrypoints against the complete main tree; inspect canonical evidence paths; assess CI coverage; prepare and red-team a fail-closed entrypoint validator.
- **Method:** GitHub read-only inspection of the complete recursive Git tree (truncated=false), registry rows and relevant source/docs; eight path-specific history queries for missing literal entrypoint paths; local temporary-Git test fixtures. No full AIEFS checkout was available locally.

## 1. Executive result

The open studies-entrypoint issue remains real on main@871417d, and the deeper scan found a parallel evidence-path integrity issue.

| Registry field | Tokens checked | Resolve in current tree | Unresolved | Affected study rows |
|---|---:|---:|---:|---:|
| canonical_entrypoints | 37 | 26 | 11 | 5 of 15 |
| canonical_evidence_paths | 33 | 22 | 11 | 6 of 15 |

The full recursive Git tree contains 3,272 entries (3,102 blobs); GitHub reports truncated=false. Results below use repository-relative, case-sensitive paths. A glob such as AIEF_1_0_*.py is interpreted at the repository root, as a normal root-relative glob with no slash would be. Matching was checked against every path in the retrieved tree, not just a hand-picked subset.

**Disposition:** this is registry/path-provenance debt, not evidence that the scientific results are false. Do not automatically replace missing names with similar files. Some likely consolidations or renamed output directories are visible, but a maintainer must establish provenance before rewriting canonical references.

## 2. canonical_entrypoints: 11 unresolved tokens

Source: registry/studies.csv blob 86a39aeaff94502cb8a549da50be4205f8a1d454. The table has 15 study rows and 37 semicolon-delimited entrypoint tokens.

| studies.csv line | Study ID | Unresolved token(s) | Finding |
|---:|---|---|---|
| 3 | AIEF_1_0_TO_1_2_FOUNDATIONAL | AIEF_1_0_*.py; AIEF_1_1_*.py; AIEF_1_2_*.py | Each root-level pattern matches zero tracked files anywhere in the retrieved tree. |
| 5 | AIEF_1_3_DISJOINT_100SEED | AIEF_1_3_sensitivity_audit_updated.py; AIEF_1_3_persistence_mechanism_test_updated.py | Neither literal path exists. Both are nevertheless named as authoritative supersession targets in registry/supersessions.csv lines 15–16. |
| 7 | AIEF_1_4_MATCHED_PHASE_ABLATION | AIEF_1_4_driver_mechanism.py | Literal path absent. The row's other code entrypoint, AIEF_1_4_matched_phase_memory_ablation.py, exists. |
| 10 | AIEF_1_4_TANGENT_AND_COCYCLE | aief_1_4_full_state_tangent_operator.py; aief_1_4_history_cocycle_test.py; aief_1_4_branch_tangent_comparison.py | All three literal paths absent. The fourth entrypoint, AIEF_1_4_frozen_driver_cocycle_analysis.py, exists. |
| 12 | AIEF_1_4_CONTROLLER_FIBER | aief_1_4_intertwining_controller.py; aief_1_4_fiber_coordinate_controller.py | Both literal paths absent. The row's AIEF_1_4_actual_admissibility_branch_audit.py and AIEF_1_4_component_controller_audit.py exist. |

### 2.1 Cross-file contradictions and possible replacements

These are leads, not certified substitutions:

- **AIEF-1.3:** registry/supersessions.csv:15–16 points to the two missing updated scripts as authoritative successors. AIEF_1_3_falsification_updated.py exists (blob 7dc1ad48585d2f2f64a5d33b89a6d3e778f3d37c, lines 1–8) and is described as a production falsification matrix, but there is no demonstrated one-to-one replacement mapping from either missing script to it. AIEF_1_3_paired_statistics_updated.py and AIEF_1_3_closure_diagnostics_updated.py are present and already listed in the row.
- **Tangent/cocycle:** registry/supersessions.csv:20 identifies the absent aief_1_4_full_state_tangent_operator.py as the authoritative target for retiring aief_1_4_operator_compression.py. history/timeline.md:35,40 and audits/scientific/SCIENTIFIC_CLASSIFICATION_AND_REJECTIONS_AUDIT.md:32–33 still describe the absent tangent/cocycle scripts as supported analysis sources. Current possible successor work includes AIEF_1_4_augmented_tangent_cocycle_analysis.py (blob 41411831e2ec7060b8423fcb21e0526adb3b3d57, lines 1–19; its docstring calls it a Stage-B augmented directional tangent cocycle) and AIEF_1_4_frozen_driver_cocycle_analysis.py (blob 91b14cccbe2290efc9d755599be964494aa08567, lines 1–18; explicitly Stage A with exogenous coherence input). Their scopes differ; do not silently treat either as identical to all three missing programs.
- **Controller/fiber:** AIEF_1_4_intertwining_controller_analysis.py exists (blob 71c0b8c5b613a1601379986bed3a060a9b35f493, lines 1–18) and AIEF_1_4_freeze_controller_fiber_theorem.py exists (blob 387ca7db94e41e579ea64af8ec435bf82a6a5a82, lines 1–10). These are plausible current code leads, not proven substitutes for the two missing entrypoint names.
- **Matched-phase:** AIEF_1_4_matched_phase_memory_ablation.py exists. The current tree also contains aief_1_4_matched_phase_memory_ablation/ as a partial output bundle and test_output/ as the complete 40-seed bundle (the row itself documents this distinction). No driver_mechanism file or directory was found.

GitHub path-specific history queries for each of the eight missing literal entrypoint names returned zero matching commits in the available repository history. This is a limited history observation, not proof that such files never existed in external or unpushed workspaces.

## 3. canonical_evidence_paths: 11 additional unresolved tokens

Source: the same registry/studies.csv blob, lines 3, 6–7, 10, 12–13. This field indexes canonical evidence locations. Unlike entrypoints, these tokens may legitimately name files or directories; the checks here allow either kind, and strip one trailing slash before comparing directory paths.

| studies.csv line | Study ID | Unresolved evidence token(s) | Context / possible current location |
|---:|---|---|---|
| 3 | AIEF_1_0_TO_1_2_FOUNDATIONAL | Papers/ | The row itself says the directory was deleted on main. GitHub path history shows removal commits for third-party papers. Treat as a known historical deletion, not an extant canonical directory. |
| 6 | AIEF_1_4_SPLIT_STATE_ABLATION | aief_1_4_frozen_history_reproduction/; aief_1_4_trajectory_recovery_equivalence/ | The second name has a plausible renamed counterpart: aief_1_4_trajectory_recovery/analysis_manifest.json (blob 20ada2f0904d450f3f317ce57745980e9b0212da, line 1) and source AIEF_1_4_trajectory_recovery_equivalence.py (blob 2a382bcfcd2971fed7c726229ac432c960b0f759, lines 1–5). Confirm the directory rename before changing the registry. No exact frozen_history_reproduction path was found. |
| 7 | AIEF_1_4_MATCHED_PHASE_ABLATION | aief_1_4_driver_mechanism/ | No path with this name exists. The row already points to test_output/; aief_1_4_matched_phase_memory_ablation/ is explicitly described as the partial attempt, so it is not a safe substitute. |
| 10 | AIEF_1_4_TANGENT_AND_COCYCLE | aief_1_4_jacobian_step_convergence/; aief_1_4_*_report.txt | No directory with the first name exists. The report glob has no root-level matches; there are nested reports in other folders, but this token does not specify recursion (**/). Current tangent outputs include aief_1_4_augmented_tangent_cocycle/analysis_manifest.json (blob 4dd0936bb5e698278e66f4634286c742c70bcae2, line 1) and aief_1_4_face_spectrum/jacobian_step_sensitivity.csv; these are leads only. |
| 12 | AIEF_1_4_CONTROLLER_FIBER | aief_1_4_k3_fiber_audit/; aief_1_4_full_seed_fiber_audit/ | Neither directory exists. Nearby extant bundles include aief_1_4_intertwining_controller 02/analysis_manifest.json (blob 0d71b14f7d2609ad30465d9a9404c44d9825904c, line 1) and aief_1_4_component_controller_audit/analysis_manifest.json (blob 67c98c22e12c01c48864b807b73662ae51aaadc5, line 1); no direct mapping is established. |
| 13 | AIEF_1_4_PROPOSAL_EQUALIZATION | aief_1_4_boundary_stress_audit/; aief_1_4_proposal_margin_audit/; aief_1_4_selection_margin_control/ | All three names are absent, but a consolidated-looking bundle exists at aief_1_4_proposal_equalization_bridge/analysis_manifest.json (blob 3f2d3e9227b7ad3c3604b28ba0095fb9c73df1df, line 1), with source AIEF_1_4_proposal_equalization_bridge_analysis.py (blob 2fcfff5ad2f594bc4fdc07e394f6bdd34deff07f, lines 1–5). Confirm file-level manifest provenance before substituting. |

A further nuance: canonical_evidence_paths has a mixed schema (files, directories and glob-like expressions). A strict validator needs explicit semantics for root-relative globs, recursion, file-vs-directory expectations and intentionally deleted historical evidence. It should not be bolted onto an entrypoint checker using the same simplistic rule.

## 4. CI and repository-side validation gap

- registry/README.md blob b3ab739359393aae5d1e02aded5d4c6885981144, line 144, describes studies.csv as the structured study index including entrypoints, evidence directories, sample design and Stage 4 targets.
- audits/engineering/verify_inventory_current.py blob 429d978258c1c9020fff94115e17bdc1d384360e, lines 74–80, checks controlled-vocabulary fields for studies.csv, but does not check whether canonical entrypoints resolve.
- .github/workflows/repo-checks.yml blob 790a1e429d01b1f17f97cada9b7db43325cec79d has no studies-entrypoint validation step.
- tools/ci/check_current_inventory.py blob 0471299194219395d8e94b12494cdccc474c192e checks artifacts_current.csv, not canonical study paths.
- Existing inbox triage row GPT6-1113-STUDY remains NEW / untriaged at audit_inbox/TRIAGE.md:166 (blob 251f4a3744d691aacc97b44607587913c6368892). This submission adds a current-main re-check and testable enforcement proposal; it does not edit the ledger.

## 5. Proposed validator and independent test strategy

A standard-library-only prototype intended for tools/ci/check_study_entrypoints.py and tests under tools/ci/tests/ is included below. It:
1. Reads registry/studies.csv using csv.DictReader; checks required fields, blank entrypoint lists, duplicate study IDs and duplicate tokens.
2. Uses git ls-files -z as the authority for tracked paths, so untracked/generated local files cannot satisfy a canonical reference.
3. Supports semicolon-delimited literal paths and root-relative globs; each token must match at least one tracked regular file.
4. Rejects absolute paths, .., backslash separators, directories in the executable-entrypoint field and symlinks resolving outside the repo root.
5. Fails closed on missing files, empty glob matches, malformed registry headers and Git enumeration failures.

**Local results (temporary Git repositories only):**
- Unit tests: 11/11 passed.
- Python bytecode compilation: PASS for checker and test module.
- A five-row fixture reconstructed from the affected canonical_entrypoints strings: 17 tokens, 11 unresolved, matching the live-tree scan. The fixture tracks placeholders for the six entries independently shown to exist; it is not a full AIEFS checkout and is not represented as one.

### CI integration sequencing

Do not turn on a strict CI gate while the 11 known entrypoint tokens remain unresolved: the gate would correctly fail current main immediately. First decide, per token, whether to restore a genuinely authoritative source, replace it with a proven successor, or explicitly classify it as historical/no-longer-applicable. Then update studies.csv and supersessions.csv together on a reviewed side branch. After that, wire the checker into the existing CI tool self-tests job or a dedicated job and retain the negative controls below.

canonical_evidence_paths needs a companion directory-aware checker after its schema semantics are made explicit (file, directory, trailing slash, glob recursion). It should not be silently treated as the same rule as executable entrypoints.

## 6. Recommended maintainer decisions

1. Reconcile the 11 canonical_entrypoints before any status/claim change. Never infer equivalence solely from similar filenames.
2. Audit the 11 canonical_evidence_paths separately. The trajectory-recovery and proposal-equalization current bundles are plausible replacements, but must be compared against manifest provenance and intended contents.
3. Correct supersessions.csv rows that currently point at absent updated/canonical targets, or restore those targets if they remain authoritative.
4. Only after the registry is internally consistent, integrate the validator and tests and add a CI step. Do not change artifact_status, evidence_scope, or scientific claims as part of this path-integrity repair.

## 7. What was not done

- No complete AIEFS clone or working tree was available. The full Git tree was fetched read-only from GitHub; the candidate validator was not run against a complete local checkout.
- No registry, supersessions, status, source, or CI files were modified on main or another branch.
- No missing sources or evidence folders were restored. No candidate alias was adopted as a replacement.
- The candidate validator tests prove behavior on controlled fixtures, not successful integration into this repository.
- The canonical_evidence_paths audit is a static tree-resolution pass; no separate evidence-path validator was executed.
- No external outreach was made.

---

# Reproducibility appendices

All code below is unverified input until a maintainer independently reviews and runs it in a full clone. It is embedded in this single Markdown submission to follow the inbox's one-file-per-review rule.

## Appendix A — candidate check_study_entrypoints.py

    #!/usr/bin/env python3
    """Candidate fail-closed validator for registry/studies.csv canonical entrypoints."""
    from __future__ import annotations
    import argparse
    import csv
    from dataclasses import dataclass
    from pathlib import Path, PurePosixPath
    import subprocess

    @dataclass(frozen=True)
    class Finding:
        study_id: str
        token: str
        reason: str

    def _safe_token(token: str) -> str | None:
        if not token:
            return "empty entrypoint token"
        if "\\" in token:
            return "backslash path separators are not permitted; use repository '/' paths"
        path = PurePosixPath(token)
        if path.is_absolute():
            return "absolute paths are not permitted"
        if any(part in ("", ".", "..") for part in token.split("/")):
            return "empty, '.' or '..' path components are not permitted"
        return None

    def validate_study_entrypoints(root: Path, csv_path: Path | None = None):
        root = root.resolve()
        if not root.is_dir():
            return [Finding("<registry>", "<root>", f"repository root is not a directory: {root}")], 0, 0
        csv_path = (csv_path or (root / "registry" / "studies.csv")).resolve()
        try:
            csv_path.relative_to(root)
        except ValueError:
            return [Finding("<registry>", str(csv_path), "registry CSV resolves outside repository root")], 0, 0
        if not csv_path.is_file():
            return [Finding("<registry>", str(csv_path), "registry CSV does not exist")], 0, 0
        try:
            tracked = subprocess.run(
                ["git", "-C", str(root), "ls-files", "-z"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            ).stdout.split(b"\0")
            tracked_files = {item.decode("utf-8", "surrogateescape") for item in tracked if item}
        except (OSError, subprocess.CalledProcessError) as exc:
            detail = getattr(exc, "stderr", b"")
            if isinstance(detail, bytes):
                detail = detail.decode("utf-8", "replace")
            return [Finding("<repository>", "<git ls-files>", f"cannot enumerate tracked paths: {detail or exc}")], 0, 0
        relative_csv = csv_path.relative_to(root).as_posix()
        if relative_csv not in tracked_files:
            return [Finding("<registry>", relative_csv, "registry CSV is not tracked by Git")], 0, 0
        findings = []
        rows_seen = tokens_seen = 0
        seen_studies = set()
        try:
            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                required = {"study_id", "canonical_entrypoints"}
                if not reader.fieldnames or not required.issubset(reader.fieldnames):
                    missing = sorted(required - set(reader.fieldnames or []))
                    return [Finding("<registry>", "<header>", f"missing required column(s): {', '.join(missing)}")], 0, 0
                for line_number, row in enumerate(reader, start=2):
                    rows_seen += 1
                    study_id = (row.get("study_id") or "").strip()
                    if not study_id:
                        findings.append(Finding(f"line {line_number}", "<study_id>", "study_id is blank"))
                        study_id = f"<line {line_number}>"
                    elif study_id in seen_studies:
                        findings.append(Finding(study_id, "<study_id>", "duplicate study_id"))
                    seen_studies.add(study_id)
                    raw = row.get("canonical_entrypoints")
                    if raw is None or not raw.strip():
                        findings.append(Finding(study_id, "<blank>", "canonical_entrypoints is blank"))
                        continue
                    tokens = [part.strip() for part in raw.split(";")]
                    if len(tokens) != len(set(tokens)):
                        findings.append(Finding(study_id, raw, "duplicate entrypoint token in row"))
                    for token in tokens:
                        tokens_seen += 1
                        error = _safe_token(token)
                        if error:
                            findings.append(Finding(study_id, token, error))
                            continue
                        has_glob = any(ch in token for ch in "*?[")
                        try:
                            candidate_paths = sorted(root.glob(token)) if has_glob else [root / token]
                        except (OSError, ValueError) as exc:
                            findings.append(Finding(study_id, token, f"invalid glob/path expression: {exc}"))
                            continue
                        candidate_paths = [p for p in candidate_paths if p.relative_to(root).as_posix() in tracked_files]
                        if not candidate_paths:
                            literal_path = root / token
                            if not has_glob and literal_path.is_dir():
                                findings.append(Finding(study_id, token, "path is a directory, not a regular file"))
                            else:
                                reason = "glob matched no tracked files" if has_glob else "path does not exist as a tracked file"
                                findings.append(Finding(study_id, token, reason))
                            continue
                        for candidate in candidate_paths:
                            try:
                                resolved = candidate.resolve(strict=True)
                                resolved.relative_to(root)
                            except FileNotFoundError:
                                findings.append(Finding(study_id, token, f"matched path is broken: {candidate.relative_to(root)}"))
                                continue
                            except ValueError:
                                findings.append(Finding(study_id, token, f"matched path resolves outside repository: {candidate.relative_to(root)}"))
                                continue
                            if not resolved.is_file():
                                findings.append(Finding(study_id, token, f"matched path is not a regular file: {candidate.relative_to(root)}"))
        except (OSError, UnicodeError, csv.Error) as exc:
            findings.append(Finding("<registry>", str(csv_path), f"cannot read registry CSV: {exc}"))
        return findings, rows_seen, tokens_seen

    def main(argv=None):
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
        args = parser.parse_args(argv)
        findings, rows, tokens = validate_study_entrypoints(args.root)
        if findings:
            print(f"FAIL: {len(findings)} finding(s) across {rows} study row(s), {tokens} entrypoint token(s)")
            for item in findings:
                print(f"  study_id={item.study_id} token={item.token!r}: {item.reason}")
            return 1
        print(f"PASS: {rows} study row(s), {tokens} canonical entrypoint token(s) resolve to repository files")
        return 0

    if __name__ == "__main__":
        raise SystemExit(main())

## Appendix B — candidate test module

    from __future__ import annotations
    import csv
    from pathlib import Path
    import tempfile
    import subprocess
    import unittest
    from check_study_entrypoints_candidate import validate_study_entrypoints

    class StudyEntrypointValidatorTests(unittest.TestCase):
        def setUp(self):
            self.temp = tempfile.TemporaryDirectory(prefix="study-entrypoints-")
            self.root = Path(self.temp.name)
            (self.root / "registry").mkdir()
            (self.root / "src").mkdir()
            subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)

        def tearDown(self):
            self.temp.cleanup()

        def write_registry(self, rows, fields=("study_id", "canonical_entrypoints")):
            path = self.root / "registry" / "studies.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(fields))
                writer.writeheader()
                writer.writerows(rows)
            subprocess.run(["git", "-C", str(self.root), "add", str(path)], check=True)
            return path

        def touch(self, relative):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# fixture\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(self.root), "add", str(path)], check=True)
            return path

        def test_literal_paths_and_multi_match_root_glob_pass(self):
            self.touch("src/one.py")
            self.touch("AIEF_1_0_alpha.py")
            self.touch("AIEF_1_0_beta.py")
            self.write_registry([{"study_id": "A", "canonical_entrypoints": "src/one.py;AIEF_1_0_*.py"}])
            findings, rows, tokens = validate_study_entrypoints(self.root)
            self.assertEqual((findings, rows, tokens), ([], 1, 2))

        def test_unmatched_literal_fails(self):
            self.write_registry([{"study_id": "A", "canonical_entrypoints": "src/missing.py"}])
            findings, _, _ = validate_study_entrypoints(self.root)
            self.assertEqual(len(findings), 1)
            self.assertIn("does not exist", findings[0].reason)

        def test_unclosed_glob_bracket_fails_without_traceback(self):
            self.write_registry([{"study_id": "A", "canonical_entrypoints": "AIEF_[broken.py"}])
            findings, _, _ = validate_study_entrypoints(self.root)
            self.assertEqual(len(findings), 1)
            self.assertTrue("glob" in findings[0].reason or "path" in findings[0].reason)

        def test_unmatched_glob_fails(self):
            self.write_registry([{"study_id": "A", "canonical_entrypoints": "AIEF_1_1_*.py"}])
            findings, _, _ = validate_study_entrypoints(self.root)
            self.assertEqual(len(findings), 1)
            self.assertIn("glob matched no", findings[0].reason)

        def test_directory_is_not_accepted_as_entrypoint(self):
            self.write_registry([{"study_id": "A", "canonical_entrypoints": "src"}])
            findings, _, _ = validate_study_entrypoints(self.root)
            self.assertEqual(len(findings), 1)
            self.assertIn("directory", findings[0].reason)

        def test_path_traversal_and_backslash_rejected(self):
            self.write_registry([{"study_id": "A", "canonical_entrypoints": "../secret.py;/tmp/absolute.py;src\\one.py"}])
            findings, _, _ = validate_study_entrypoints(self.root)
            self.assertEqual(len(findings), 3)
            self.assertTrue(all("not permitted" in f.reason for f in findings))

        def test_symlink_escape_rejected(self):
            outside = Path(self.temp.name).parent / (Path(self.temp.name).name + "-outside.py")
            outside.write_text("# outside\n", encoding="utf-8")
            try:
                (self.root / "escape.py").symlink_to(outside)
                subprocess.run(["git", "-C", str(self.root), "add", "escape.py"], check=True)
                self.write_registry([{"study_id": "A", "canonical_entrypoints": "escape.py"}])
                findings, _, _ = validate_study_entrypoints(self.root)
                self.assertEqual(len(findings), 1)
                self.assertIn("outside repository", findings[0].reason)
            finally:
                outside.unlink(missing_ok=True)

        def test_untracked_file_does_not_satisfy_entrypoint(self):
            self.write_registry([{"study_id": "A", "canonical_entrypoints": "src/one.py"}])
            untracked = self.root / "src" / "one.py"
            untracked.write_text("# not staged\n", encoding="utf-8")
            findings, _, _ = validate_study_entrypoints(self.root)
            self.assertEqual(len(findings), 1)
            self.assertIn("does not exist", findings[0].reason)

        def test_missing_required_column_fails_closed(self):
            self.write_registry([{"study_id": "A"}], fields=("study_id",))
            findings, rows, tokens = validate_study_entrypoints(self.root)
            self.assertEqual(rows, 0)
            self.assertEqual(tokens, 0)
            self.assertIn("canonical_entrypoints", findings[0].reason)

        def test_duplicate_entrypoint_token_reported(self):
            self.touch("src/one.py")
            self.write_registry([{"study_id": "A", "canonical_entrypoints": "src/one.py;src/one.py"}])
            findings, _, _ = validate_study_entrypoints(self.root)
            self.assertEqual(len(findings), 1)
            self.assertIn("duplicate entrypoint token", findings[0].reason)

        def test_duplicate_study_id_and_blank_entrypoints_reported(self):
            self.touch("src/one.py")
            self.write_registry([
                {"study_id": "A", "canonical_entrypoints": "src/one.py"},
                {"study_id": "A", "canonical_entrypoints": ""},
            ])
            findings, rows, _ = validate_study_entrypoints(self.root)
            self.assertEqual(rows, 2)
            self.assertEqual(len(findings), 2)
            self.assertTrue(any("duplicate study_id" in f.reason for f in findings))
            self.assertTrue(any("is blank" in f.reason for f in findings))

    if __name__ == "__main__":
        unittest.main(verbosity=2)

## Appendix C — test results and fixture summary

    test_directory_is_not_accepted_as_entrypoint ... ok
    test_duplicate_entrypoint_token_reported ... ok
    test_duplicate_study_id_and_blank_entrypoints_reported ... ok
    test_literal_paths_and_multi_match_root_glob_pass ... ok
    test_missing_required_column_fails_closed ... ok
    test_path_traversal_and_backslash_rejected ... ok
    test_symlink_escape_rejected ... ok
    test_unclosed_glob_bracket_fails_without_traceback ... ok
    test_unmatched_glob_fails ... ok
    test_unmatched_literal_fails ... ok
    test_untracked_file_does_not_satisfy_entrypoint ... ok

    ----------------------------------------------------------------------
    Ran 11 tests in 0.110s

    OK

    fixture_rows=5 tokens=17 findings=11

The fixture is synthetic and limited to the five affected entrypoint rows. Six present entries are represented by tracked placeholder files; all 11 unresolved tokens match the current-tree re-check. This is not execution against a full AIEFS clone.

