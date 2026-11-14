# AIEF Modular Experiment Driver Platform v1 — Scaffold Implementation Report

## Status

**Implemented as an unverified scaffold; not production ready.**

The authoritative engine, original driver, analysis source, frozen baseline artifacts, and successful `T_window` oracle run were not present in the workspace. At the user's direction, the modular platform was implemented from the supplied specifications. Static/unit testing was completed, but numerical smoke, frozen-baseline, selected-oracle, and full-oracle acceptance gates remain unexecuted.

## 1. New files created

### Platform package

- `aief_modular/__init__.py`
- `aief_modular/spec.py`
- `aief_modular/registry.py`
- `aief_modular/factors.py`
- `aief_modular/branches.py`
- `aief_modular/collectors.py`
- `aief_modular/validation.py`
- `aief_modular/artifacts.py`
- `aief_modular/runner.py`
- `aief_modular/catalog.py`
- `aief_modular/oracle.py`
- `aief_modular/studies/__init__.py`
- `aief_modular/studies/aief_1_4_s01_twindow.py`

### CLI and documentation

- `AIEF_modular_driver_v1.py`
- `README_modular.md`
- `MODULAR_IMPLEMENTATION_REPORT.md`
- `pytest.ini`

### Tests

- `tests_modular/conftest.py`
- `tests_modular/test_spec_canonicalization.py`
- `tests_modular/test_registry.py`
- `tests_modular/test_condition_expansion.py`
- `tests_modular/test_rng_namespace.py`
- `tests_modular/test_artifact_paths.py`
- `tests_modular/test_atomic_writes.py`
- `tests_modular/test_catalog.py`
- `tests_modular/test_unsupported_policies.py`
- `tests_modular/test_builtin_registry.py`
- `tests_modular/test_twindow_one_condition.py`
- `tests_modular/test_twindow_oracle_equivalence.py`

## 2. Existing files modified

None. The protected production sources and run directories were absent from the workspace and were neither created nor modified.

## 3. CLI examples

```bash
python AIEF_modular_driver_v1.py list-studies
python AIEF_modular_driver_v1.py describe AIEF_1_4_S01
python AIEF_modular_driver_v1.py dry-run AIEF_1_4_S01
```

```bash
python AIEF_modular_driver_v1.py baseline-only AIEF_1_4_S01 \
  --frozen-manifest runs/5a9f093a2fe0/manifest.json \
  --frozen-npz runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz \
  --frozen-scalar runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv \
  --output-root experiments
```

```bash
python AIEF_modular_driver_v1.py run AIEF_1_4_S01 \
  --frozen-manifest runs/5a9f093a2fe0/manifest.json \
  --frozen-npz runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz \
  --frozen-scalar runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv \
  --output-root experiments
```

```bash
python AIEF_modular_driver_v1.py catalog --output-root experiments
python AIEF_modular_driver_v1.py catalog --output-root experiments --replace-catalog
```

There is no skip-baseline or overwrite option. `--resume` fails explicitly because resume is unsupported in v1.

## 4. Package/module diagram

```text
AIEF_modular_driver_v1.py
    |
    +-- registry.py ---- studies/aief_1_4_s01_twindow.py
    |                         |
    |                         +-- imports authoritative engine ModelConfig
    |
    +-- runner.py
          +-- spec.py          immutable records + canonical identities
          +-- factors.py       rho resolution + condition expansion
          +-- branches.py      engine-v1 branch/RNG compatibility
          +-- collectors.py    legacy T_window CSV/NPZ contract
          +-- validation.py    typed validation gates/exceptions
          +-- artifacts.py     atomic I/O, paths, locks, hashing
          +-- catalog.py       derived non-authoritative catalog

oracle.py                    decompressed logical oracle comparator
```

No numerical step-map code is copied into the platform. Prefix and future simulation delegate to `aief_experiment_engine_v1`.

## 5. Canonical identity payload

`spec.py` provides deterministic canonical JSON with:

- sorted mapping keys;
- declared tuple/list order preserved;
- compact UTF-8 JSON;
- Python round-trip float representation;
- rejection of NaN and Infinity;
- no timestamp, output root, host, environment, absolute path, or object `repr`.

The scientific identity payload contains:

- identity schema ID;
- study ID and version;
- complete canonical `ExperimentSpec`;
- full specification SHA-256;
- logical-name-to-source-hash mapping;
- exact paired seeds and generation rule;
- factor level IDs, values, and metadata;
- protocol;
- full branch RNG namespace;
- executed branches;
- collector IDs and schema versions.

`scientific_identity_sha256` is the full SHA-256. Its first 16 characters form the human-facing `run_id`. Execution mode, timestamp, nonce, output path, and environment are excluded.

Execution identity is separate:

```text
baseline_YYYYMMDDTHHMMSSZ_<8 hex chars>
production_YYYYMMDDTHHMMSSZ_<8 hex chars>
```

## 6. Output directory specification

```text
experiments/
  AIEF_1_4_S01_twindow_sensitivity/
    v1/
      <16-char-run-id>/
        baseline|production/
          <execution-id>/
            manifest.json
            baseline_equivalence_certificate.json
            baseline_equivalence_by_seed.json
            twindow_condition_status.csv
            AIEF_1_4_Twindow_sensitivity_<run-id>_scalar_summary.csv
            AIEF_1_4_Twindow_sensitivity_<run-id>_branch_diagnostics.npz
            conditions/
              condition_seed_<seed>_rho_<level>.npz
            logs/
            analysis/
            failure/
```

The manifest and consolidated CSV/NPZ are authoritative. Checkpoints are marked diagnostic and non-authoritative. Catalogs are derived indexes.

## 7. Study registry contents

```text
AIEF_1_4_S01  twindow_sensitivity  v1  AIEF-1.4 T_window Sensitivity
```

The registry rejects duplicate IDs and duplicate slugs, lists deterministically, and imports only package-owned study modules.

The study declares:

- 40 exact paired seeds from master seed `20260714`;
- rho levels in order `0.5, 0.75, 1.0, 1.5, 2.0`;
- full regeneration for every seed/rho condition;
- 200 conditions and 800 scalar rows;
- full seven-branch RNG namespace;
- executed branches `continue`, `reset_ema`, `reset_B`, `future_shuffle`;
- `future_shuffle` child index 6 (the seventh child).

## 8. Validation and failure model

Typed failures:

- `SpecValidationError`
- `BaselineGateError`
- `ConditionSchemaError`
- `ArtifactIntegrityError`
- `UnsupportedPolicyError`
- `ExecutionLockError`
- `CatalogError`

Validation includes immutable-spec invariants, engine API compatibility, unsupported-policy rejection, exact condition expansion, prefix shape/dtype/finiteness, engine matrix schema, exact diagnostic schedule, trajectory ranges, exact horizon metadata, finite primary/secondary outcomes, exact branch set/order, output-key collision checks, and final count checks.

Execution uses a create-only lock containing PID, host, and start time. Existing locks are never stolen. JSON, CSV, NPZ, text, condition status, and manifests use temporary files, file `fsync`, atomic replacement, and directory `fsync`.

On failure, the runner stops globally, preserves committed checkpoints, writes a traceback, updates `manifest.json`, writes `FAILED_manifest.json`, records condition ID and committed status count, sets `freezeable=false`, and exits nonzero.

Condition status is atomically replaced after each committed condition. It is crash diagnostics, not resume support.

## 9. Tests run and exact results

### Compilation

```text
python -m compileall -q aief_modular AIEF_modular_driver_v1.py tests_modular
COMPILE_OK
```

### Unit/static suite

```text
pytest -q
15 passed, 2 skipped in 0.06s
```

The two skipped tests are the numerical one-condition smoke and full oracle comparison; they require absent authority files.

### Registry command

```text
AIEF_1_4_S01  twindow_sensitivity  v1  AIEF-1.4 T_window Sensitivity
```

### Structural dry-run with a temporary nonnumerical engine stub

```text
status=validated
seed_count=40
condition_count=200
scalar_row_count=800
future_shuffle_rng_child_index=6
```

Two repeated dry-runs produced the same run ID. This stub was outside the workspace and was used only to exercise orchestration/static identity; it is not a numerical validation.

### Failure-path test with a temporary failing baseline stub

```text
exit code: 4
FAILED_manifest status: failed
freezeable: false
exception type: BaselineGateError
traceback recorded: yes
```

## 10. One-condition smoke result

**Not executed.** The test exists and is skipped unless both conditions are met:

```bash
AIEF_RUN_SLOW_TESTS=1 pytest -q tests_modular/test_twindow_one_condition.py
```

and `aief_experiment_engine_v1.py` is importable.

The smoke uses the first frozen seed at rho `0.5`, regenerates the prefix, runs all four study branches with the full seven-branch RNG namespace, validates the schema, and performs a checkpoint round trip.

## 11. Baseline certificate result

**Not executed.** The frozen engine and baseline authority artifacts were unavailable. No claim of 40/40 or 7/7 certification is made.

## 12. Oracle-comparison result

**Not executed.** `runs/b57562a8ee77/` and a completed modular run were unavailable.

The logical comparator in `aief_modular/oracle.py` compares:

- scalar columns, row order, condition keys, and exact NaN-aware scalar values;
- complete NPZ key sets;
- decompressed array shapes, dtypes, NaN positions, and exact values;
- condition-status coverage.

It never compares compressed NPZ file bytes.

To run after producing a modular leaf execution:

```bash
AIEF_MODULAR_RUN=<modular-leaf> \
AIEF_TWINDOW_ORACLE=runs/b57562a8ee77 \
pytest -q tests_modular/test_twindow_oracle_equivalence.py
```

## 13. Remaining unsupported features

- Resume or checkpoint continuation
- Certificate reuse
- Arbitrary path-loaded plugins
- Arbitrary state interventions
- New noise or forcing policies
- `dt`, `tau`, or safeguard study resolvers
- Operator/model changes under engine v1
- Parallel condition execution
- Any collector beyond `TWindowLegacyCollectorV1`
- Any registered study beyond `AIEF_1_4_S01`

These fail explicitly or have no interface exposed as working functionality.

## 14. Known limitations and next safe extension

1. Integrate this scaffold into the authoritative repository without replacing protected sources.
2. Run real `list-studies`, `describe`, and `dry-run` against the certified engine.
3. Execute the one-condition rho=0.5 smoke.
4. Run the complete 40-seed/seven-branch baseline gate.
5. Run selected oracle comparisons for at least two seeds, including `4619122171158768524`, over all rho levels and branches.
6. Run the full 200-condition modular execution and logical oracle comparison.
7. Only after all gates pass, consider a compatibility wrapper or replacement designation.

The first safe functional extension after certification would be another declarative **model-regime factor** supported by an unchanged engine configuration interface. It should receive its own resolver ID, study specification, collector schema, and oracle tests. Operator changes must instead create a new engine/model version.
