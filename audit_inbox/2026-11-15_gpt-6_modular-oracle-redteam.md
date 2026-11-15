# GPT-6 outside-audit note — modular T-window oracle false-pass paths

> **UNVERIFIED INPUT.** Independent source review and red-team finding for maintainer triage. This is not an owner decision, production certification, code change, or claim that a real modular run passed. No repository files were edited. No real simulation or full oracle comparison was executed.

- **Agent / model:** GPT-6
- **Date:** 2026-11-15 (Europe/Tirane)
- **Main reviewed:** `ade1179f049bca0a7de3a1152880a2c6e0a19db4`
- **Scope:** Inspect the modular S01 oracle-equivalence test and its comparator versions for conditions under which the check could report success without independently validating a newly generated modular execution.
- **Method:** Read-only inspection of source, workflow and errata; compare the pinned legacy comparator with its opt-in successor; derive a negative-control invocation. This review used GitHub source fetches, not a complete local clone.

## Executive finding

The repository already correctly says the modular platform is **not oracle-certified**. This audit found two concrete false-pass paths in the optional equivalence test, plus a third provenance gap that prevents a passing comparison from certifying that its candidate was a genuine modular production execution:

1. **It imports the legacy comparator, despite E21 documenting a known false-PASS defect in that comparator.** The active optional test at `tests_modular/test_twindow_oracle_equivalence.py:8` imports `aief_modular.oracle.compare_twindow_run`. E21 explicitly records that this function can return `status='passed'` when the candidate contains an extra duplicate `(seed,rho,status)` row. E21 provides `oracle_v1_1.py` as the corrected opt-in successor, but the optional equivalence test has not switched to it.
2. **It does not reject candidate/reference self-comparison.** The test only checks that both configured paths exist. Neither the test nor either comparator version checks that the candidate and oracle resolve to different directories/files. Setting `AIEF_MODULAR_RUN` and `AIEF_TWINDOW_ORACLE` to the same S01 oracle directory makes the comparator compare each output with itself; with the reference's established 800 scalar rows and 200 condition rows, the test's final count assertions are satisfied. The corrected v1.1 duplicate-row check does not fix this identity problem.
3. **It does not validate candidate execution provenance.** The comparator does not parse the candidate manifest, verify a production execution status, or bind the compared scalar/NPZ/status files to the hashes recorded by that manifest. A copied oracle bundle placed at another path can therefore pass a path-distinctness check without proving that a modular production run generated it.

These are test-design gaps, not evidence that the modular engine itself is numerically wrong. The current CI/default behavior continues to skip the full oracle-equivalence test unless the required run paths are supplied. Therefore the correct overall status remains **not oracle-certified**. The current claim wording in `AUD-MODULAR-ORACLE` is appropriately cautious; this note recommends closing the gate, not promoting the claim.

## 1. Evidence and provenance

All paths below are on `main` at the reviewed tip unless otherwise stated.

| Evidence | Blob SHA | Relevant location | Finding |
|---|---|---:|---|
| `tests_modular/test_twindow_oracle_equivalence.py` | `befa41e25fae952a830909ba6d1313b88af56945` | lines 8, 11–25 | Imports legacy `oracle`, returns `skip` if candidate path is unset/missing or oracle path missing; no distinct-path assertion; compares candidate and oracle and then checks 800/200 counts. |
| `aief_modular/oracle.py` | `d2c59fe2ded5c842fcfd56dd8819f50cc55dc434` | lines 97–111, 123–145 | Legacy coverage comparison uses sets, losing row multiplicity; comparator does not reject identical candidate and oracle paths. |
| `aief_modular/oracle_v1_1.py` | `0749cec73b3c1b1b12ea4d21f16752230aaece7e` | lines 97–111, 123–145 | Adds equal-row-count and unique `(seed,rho)` checks on both sides; still does not reject identical candidate and oracle paths. |
| `ERRATA_2026-10-28.md` | `bdfa3b3c0eb15d2f15787ef52e0399aedd56a43d` | E21, lines 527–552 | Documents the legacy duplicate-row false-PASS and explicitly recommends opting in to `oracle_v1_1`; states pinned old comparator is not edited and consumers are not silently switched. |
| `tests_modular/test_040282_f4_f6_f7.py` | `5f35b5e784cfd8ca1385bfebf36616f97e249af8` | lines 141–175 | Regression test deliberately proves legacy comparator passes the added-duplicate mutant and v1.1 rejects it. This test is evidence for the defect, but the active oracle integration test still imports legacy. |
| `aief_modular/runner.py` | `9e3eb431444f3f32b3b3e616014332939bf0ea59` | lines 227–248, 731–755 | A real completed modular execution has a manifest schema, `execution_mode`, `status='completed'`, `freezeable=True`, completion counts and output hashes; the comparator does not validate this provenance. |
| `MODULAR_IMPLEMENTATION_REPORT.md` | `0f93587539682a0731e859041392e84a071f9f37` | lines 237–337 | Report says the oracle comparison was **not executed** because the oracle and completed modular run were unavailable; no claim of 40/40 or 7/7 certification is made. |
| `.github/workflows/repo-checks.yml` | `790a1e429d01b1f17f97cada9b7db43325cec79d` | lines 202–208 | Default modular suite runs in CI; comment expects 43 passed, 2 skipped and 2 xfailed. The oracle-equivalence test is skipped unless configured paths are supplied. |

## 2. Finding A — active optional test still calls the known-defective legacy comparator

The active test imports:

```python
from aief_modular.oracle import compare_twindow_run
```

The environment resolver returns the candidate path directly from `AIEF_MODULAR_RUN` and defaults the oracle to `runs/b57562a8ee77`. If either required directory is unavailable, it skips. Otherwise, it calls the imported legacy comparator and checks `status == 'passed'`, `scalar_rows == 800`, and `condition_rows == 200`.

E21 already specifies a known false-PASS witness for that legacy comparator: with two condition rows in the reference and the same two plus one duplicate in the candidate, set equality reports `passed` and returns `condition_rows=3`. The regression test at `test_040282_f4_f6_f7.py:141–149` explicitly locks this behavior in the legacy function and demonstrates the v1.1 successor rejects it.

The presence of a correct comparator is not enough if the test used as the optional integration gate still imports the old one. The reason in E21 for not silently switching pinned consumers does not prevent a separately-versioned test consumer from explicitly opting into `oracle_v1_1`.

**Disposition:** a concrete integration-test gap. Do not edit hash-pinned `oracle.py`. The test should import `compare_twindow_run` from `aief_modular.oracle_v1_1`, and an integration regression should preserve the E21 duplicate mutant as a required failure.

## 3. Finding B — candidate/reference self-comparison is accepted

The test's `_paths()` simply builds the two `Path` values from environment variables. There is no check that their resolved paths differ. `oracle.py` and `oracle_v1_1.py` both construct `candidate = Path(candidate_dir)` and `oracle = Path(oracle_dir)` and immediately locate/compare the same named files. Neither checks `resolve()`, `samefile()`, or equivalent identity.

Therefore, when both environment variables point at the reference directory, the files are pairwise identical by construction. The test's scalar-row and condition-row count checks do not establish that a modular run was independently generated; they only check the number of rows in the self-comparison. This remains true after switching to v1.1.

A concrete negative-control command, to be run from the modular platform directory in a complete checkout, is:

```bash
ORACLE="$(realpath ../../runs/b57562a8ee77)"
AIEF_MODULAR_RUN="$ORACLE" \
AIEF_TWINDOW_ORACLE="$ORACLE" \
python -m pytest -q tests_modular/test_twindow_oracle_equivalence.py
```

**Expected behavior of the current test by static inspection:** it will execute rather than skip, compare the reference directory with itself, and pass if that reference contains the documented 800 scalar rows and 200 condition rows. This exact command was **not run** in this environment because the repository checkout and run artifacts are not mounted here. It is a derived negative control, not an observed test result.

**Disposition:** add a fail-closed candidate/oracle identity check in the test and comparator. It should reject identical resolved paths and same-file aliases (for example, symlinks). Keep this guard in the new opt-in comparator rather than editing the pinned legacy comparator.

## 4. Provenance check is also missing from the comparator contract

The comparator compares the scalar CSV, decompressed NPZ contents, and condition-status CSV. It does not parse or validate a candidate `manifest.json`. The modular runner's successful execution manifest contains useful provenance fields: schema `aief-modular-execution-manifest-v1`, study identity/version, `execution_mode`, run/execution IDs, status, `freezeable`, completion counts and `output_hashes` (runner blob `9e3eb...`, lines 227–248 and 731–755).

For an engine-equivalence test to certify a generated modular run, the integration layer should validate that the candidate is a completed production execution and that the candidate artifacts actually match the hashes recorded in that candidate manifest before comparing them with the independent oracle. Merely having files with the expected wildcard names is not proof that the candidate came from a modular execution. A copied baseline directory under a different path would also evade a path-only identity check.

Recommended candidate checks (in addition to comparator equality):

- manifest schema is `aief-modular-execution-manifest-v1`;
- `execution_mode` is the production mode;
- `status == 'completed'`, `freezeable is True`, `completion.freezeable is True`, zero failed conditions;
- expected S01 scientific identity/specification and the complete expected 200-condition / 800-scalar row counts;
- SHA-256 of the candidate scalar CSV, diagnostics NPZ and condition-status CSV equals the candidate manifest's `output_hashes`;
- candidate output directory is distinct from the oracle and is an actual modular production leaf.

These checks establish that the object being compared is a valid modular output. The comparison against a separately pinned frozen oracle remains a distinct check.

## 5. Minimal remediation plan

1. In a separately-versioned test change, import `oracle_v1_1.compare_twindow_run` in `tests_modular/test_twindow_oracle_equivalence.py`; leave the pinned `oracle.py` byte-identical.
2. In the v1.1 comparator, reject identical resolved candidate/oracle paths and same-file aliases before reading artifacts. Add tests for equal paths, a symlink alias, and two genuinely distinct directories.
3. In the integration test, validate the candidate's modular execution manifest and its output hashes before calling the comparator. Reject an oracle directory passed as candidate, even if its files have all the expected names and row counts.
4. Add an explicit red-team test using the oracle directory itself as the candidate. It must fail before comparison; it must not pass or silently skip.
5. After the guards land, run the real one-condition engine smoke, a real modular leaf execution, and the full logical oracle test against `runs/b57562a8ee77`. Keep the result labelled not certified until those actual data-bearing checks pass and are independently reviewed.

No claim-status promotion is recommended now. The existing `AUD-MODULAR-ORACLE` caution is supported by the source/report evidence.

## 6. What was and was not done

**Read:** source code, E21 erratum, regression suite, runner manifest construction, CI job and modular implementation report at the SHAs above.

**Not run:** full repository CI, `pytest`, real engine smoke, full modular execution, oracle comparison, or the proposed self-comparison command. No real trajectory or S01 artifact was opened. The exact expected self-comparison pass is inferred from the comparator/test control flow and the documented row counts, not claimed as executed.

**Not changed:** `main`, hash-pinned files, workflow, legacy comparator, v1.1 comparator, tests, registry, inbox triage or the Arena branch.

---

## Appendix — suggested regression tests

These are acceptance tests for a future patch, not tests that have been integrated or run against AIEF:

```python
def test_oracle_comparator_rejects_same_directory(tmp_path):
    run = make_complete_oracle_fixture(tmp_path / "run")
    with pytest.raises(ArtifactIntegrityError, match="candidate.*oracle.*same"):
        oracle_v1_1.compare_twindow_run(run, run)


def test_oracle_comparator_rejects_symlink_alias(tmp_path):
    run = make_complete_oracle_fixture(tmp_path / "run")
    alias = tmp_path / "alias"
    alias.symlink_to(run, target_is_directory=True)
    with pytest.raises(ArtifactIntegrityError, match="candidate.*oracle.*same"):
        oracle_v1_1.compare_twindow_run(run, alias)


def test_oracle_integration_rejects_reference_as_candidate(monkeypatch, oracle_dir):
    monkeypatch.setenv("AIEF_MODULAR_RUN", str(oracle_dir.resolve()))
    monkeypatch.setenv("AIEF_TWINDOW_ORACLE", str(oracle_dir.resolve()))
    with pytest.raises(ArtifactIntegrityError):
        run_oracle_equivalence_gate()


def test_oracle_integration_rejects_candidate_artifact_hash_mismatch(...):
    # Mutate one output after a successful modular run without updating its manifest.
    # The candidate manifest/output-hash gate must fail before logical comparison.
    ...
```
