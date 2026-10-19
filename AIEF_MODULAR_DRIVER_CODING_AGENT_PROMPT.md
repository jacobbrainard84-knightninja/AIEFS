# Coding-Agent Instructions: AIEF Modular Experiment Driver Platform v1

## 0. Role and objective

You are implementing a **new, versioned modular experiment-driver platform** for AIEF. The goal is to extract reusable experiment orchestration from the successful `T_window` study without changing the validated numerical dynamics.

The current architecture already has three layers:

1. `aief_experiment_engine_v1.py` — numerical dynamics, state, RNG hierarchy, replay, branch simulation, diagnostics, and frozen-baseline equivalence.
2. `AIEF_1_4_Twindow_sensitivity.py` — study protocol and orchestration.
3. `AIEF_1_4_Twindow_sensitivity_analysis_v3.py` — estimands and statistical analysis.

Your task is to modularize the **middle layer**. Build a general runner plus declarative study specifications so future studies can reuse the same certified engine and artifact machinery.

The first and mandatory reference implementation is the existing `T_window` sensitivity study. The modular version must reproduce the current driver’s scientific behavior and data products.

---

## 1. Non-negotiable constraints

### 1.1 Do not modify frozen or successful production sources

Do **not** edit or overwrite:

```text
aief_experiment_engine_v1.py
AIEF_1_4_Twindow_sensitivity.py
AIEF_1_4_Twindow_sensitivity_analysis_v3.py
AIEF_1_4_memory_ablation_updated.py
runs/5a9f093a2fe0/
runs/b57562a8ee77/
```

Treat these as authorities/oracles. Add new files. If a compatibility wrapper is eventually desired, create it only after the modular implementation has passed equivalence testing.

### 1.2 Do not change the numerical model

The modularization must not alter:

```text
N
dt
tau
omega
eta
mu
gamma
capacity
B_c
B_init_scale
T_window semantics
delay indexing
EMA update
positivity map
symmetrization
global gate
minimum.outer endpoint scaling
fixed +1e-12 safeguard
RNG streams
seed pairing
split-state protocol
branch RNG namespace
trajectory sampling schedule
```

Do not rewrite the step map. Import and call the existing engine.

### 1.3 Do not represent every change as a state intervention

Use four distinct categories:

1. **Model-regime factors** — modify `ModelConfig` before initialization and require full regeneration. Examples: `T_window`, `dt`, `tau`, safeguard epsilon.
2. **State interventions** — transform a state at a scheduled protocol event. Examples: reset EMA, reset B, reset phase/history.
3. **Dynamic forcing policies** — modify a driver during future stepping. Example: `future_shuffle`.
4. **Operator/model changes** — changes to the actual admissibility rule, mirror dynamics, delay law, etc. These require a new engine/model version and are not ordinary plugins under engine v1.

`T_window` scaling is a model-regime factor, not a split-state intervention.

### 1.4 Full regeneration policy

A changed `T_window`, `dt`, `tau`, safeguard, or any model parameter requires a fresh trajectory from initialization. Never reuse a split state across incompatible model configurations.

### 1.5 Inferential unit

The seed/graph is the inferential unit. Branches, factor levels, edges, components, horizons, perturbation directions, and repeated runs within a seed are paired measurements, not independent replicates.

### 1.6 No fake feature support

Engine v1 exposes only its current branch/intervention behavior. Do not claim that arbitrary noise, forcing, delay changes, or user-defined interventions are supported unless the existing engine can actually execute them without modification.

Define compatibility interfaces and fail clearly for unsupported policies. Do not silently implement a different numerical model in the runner.

---

## 2. Existing authorities and golden references

### 2.1 Frozen baseline authority

```text
runs/5a9f093a2fe0/manifest.json
runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_branch_diagnostics.npz
runs/5a9f093a2fe0/AIEF_1_4_5a9f093a2fe0_scalar_summary.csv
```

### 2.2 Successful production `T_window` oracle

```text
runs/b57562a8ee77/
```

The successful run established:

```text
40/40 frozen seeds passed baseline equivalence
7/7 frozen branches passed
200/200 regenerated (seed, rho) conditions succeeded
800 branch-level scalar rows
freezeable = true
```

Use its manifest, scalar CSV, consolidated NPZ, condition checkpoints, and certificate as golden reference data. Do not interpret a repeated equivalence run as an independent experiment.

### 2.3 Compatibility requirement

For the modular `T_window` implementation, compare logical contents, not compressed-file bytes:

- scalar row identity and ordering;
- exact seed, rho, and branch keys;
- exact scalar values with NaN-aware equality;
- exact array shape, dtype, and NaN-aware values;
- exact branch RNG assignment;
- exact prefix and future outputs;
- exact horizon metadata;
- exact condition-status coverage.

Do not require NPZ file SHA-256 equality because compression/container metadata may differ. Compare arrays after loading.

---

## 3. Required new file structure

Create a new package; do not turn the current driver into another monolith.

Recommended structure:

```text
aief_modular/
    __init__.py
    spec.py
    registry.py
    factors.py
    branches.py
    collectors.py
    validation.py
    artifacts.py
    runner.py
    catalog.py
    studies/
        __init__.py
        aief_1_4_s01_twindow.py

AIEF_modular_driver_v1.py
```

Tests:

```text
tests_modular/
    test_spec_canonicalization.py
    test_registry.py
    test_condition_expansion.py
    test_rng_namespace.py
    test_artifact_paths.py
    test_atomic_writes.py
    test_twindow_one_condition.py
    test_twindow_oracle_equivalence.py
```

If the repository does not use pytest, provide an equivalent deterministic self-test script, but pytest is preferred if already available.

---

## 4. Core data model

All specification objects must be immutable dataclasses or equivalent immutable records. They must have deterministic canonical serialization.

### 4.1 `ExperimentSpec`

Implement an immutable specification containing at least:

```python
@dataclass(frozen=True)
class ExperimentSpec:
    study_id: str
    study_slug: str
    study_version: str
    title: str
    purpose: str
    engine_module: str
    base_model: ModelConfig
    model_axes: tuple[ModelFactorSpec, ...]
    protocol: ProtocolSpec
    seed_design: SeedDesignSpec
    branch_rng_namespace: tuple[str, ...]
    branches: tuple[BranchSpec, ...]
    collectors: tuple[CollectorSpec, ...]
    baseline_gate: BaselineGateSpec
    artifact_policy: ArtifactPolicySpec
    validators: tuple[ValidatorSpec, ...]
```

Requirements:

- validate uniqueness of factor names, branch names, level IDs, and collector names;
- require `continue` when downstream metrics need a continue reference;
- require executed branches to be a subset of the branch RNG namespace;
- preserve RNG namespace order exactly;
- require positive finite times and valid protocol ordering;
- require a reference factor level where applicable;
- reject unsupported engine policies before any simulation.

### 4.2 Canonical serialization

Implement a function equivalent to:

```python
canonical_json(spec) -> str
```

Requirements:

- sorted dictionary keys;
- stable list ordering;
- no NaN or Infinity;
- full-precision float representation;
- no absolute source paths;
- no timestamps;
- no platform/environment data;
- no output-root path;
- no Python object repr strings.

Use canonical JSON to compute `spec_sha256`.

### 4.3 Scientific run identity

Compute a deterministic scientific `run_id` from a canonical identity payload containing:

- study ID and version;
- canonical experiment specification;
- engine source hash;
- runner source hash;
- all study/plugin source hashes;
- exact paired seed list and seed-generation rule;
- model factor levels;
- protocol;
- branch RNG namespace;
- executed branches;
- collectors and schema versions.

Do not include:

- absolute paths;
- host platform;
- Python environment strings;
- timestamp;
- baseline-only versus production execution mode.

Use a 12- or 16-character prefix for human-facing paths, but retain the full SHA-256 in the manifest.

### 4.4 Execution identity

Baseline-only and production executions of the same scientific specification must not collide.

Use a separate `execution_id`, for example:

```text
baseline_20260810T153000Z_<short nonce>
production_20260810T170000Z_<short nonce>
```

The timestamp/nonce belongs to execution provenance, not scientific identity.

---

## 5. Study registry

Implement an explicit registry with unique IDs.

Example:

```python
register_study(
    "AIEF_1_4_S01",
    build_twindow_spec,
)
```

Registry requirements:

- duplicate IDs are fatal;
- duplicate slugs are fatal;
- registry listing is deterministic;
- registry entries expose ID, slug, version, title, and source module;
- no arbitrary dynamic code loading from untrusted file paths;
- each registered study can produce a validated `ExperimentSpec`.

Required CLI operations:

```bash
python AIEF_modular_driver_v1.py list-studies
python AIEF_modular_driver_v1.py describe AIEF_1_4_S01
python AIEF_modular_driver_v1.py dry-run AIEF_1_4_S01
python AIEF_modular_driver_v1.py baseline-only AIEF_1_4_S01 ...
python AIEF_modular_driver_v1.py run AIEF_1_4_S01 ...
python AIEF_modular_driver_v1.py catalog --output-root experiments
```

---

## 6. Model-factor interface

Implement a typed model-factor abstraction.

```python
@dataclass(frozen=True)
class ModelFactorSpec:
    name: str
    levels: tuple[FactorLevel, ...]
    reference_level_id: str
    regeneration_policy: str
```

Each `FactorLevel` must have:

```python
level_id: str       # stable machine ID, e.g. "rho_0p50"
label: str          # human label, e.g. "rho=0.5"
value: float
metadata: mapping
```

Implement a resolver that maps `(base_model, level)` to a new immutable `ModelConfig`.

For `T_window`:

```python
T_window = rho * T_star
alpha = exp(-dt / T_window)  # derived by engine config
regeneration_policy = "full_from_initialization"
```

The runner must reject split-state reuse when the policy is full regeneration.

Do not add `dt`, `tau`, or safeguard studies now. Only create interfaces and compatibility failures for future implementation.

---

## 7. Branch and intervention interface

For engine v1, use explicit mappings to supported engine branch names.

```python
@dataclass(frozen=True)
class BranchSpec:
    name: str
    engine_branch: str
    role: str
    intervention_ids: tuple[str, ...]
    forcing_policy_id: str | None
    requires_rng: bool
```

Initial supported mapping:

```text
continue       -> engine branch continue
reset_ema      -> engine branch reset_ema
reset_B        -> engine branch reset_B
future_shuffle -> engine branch future_shuffle
```

The `T_window` study must retain the full frozen namespace:

```python
(
    "continue",
    "reset_ema",
    "reset_B",
    "reset_B_ema",
    "B_carrier_only",
    "full_reset",
    "future_shuffle",
)
```

while executing only:

```python
(
    "continue",
    "reset_ema",
    "reset_B",
    "future_shuffle",
)
```

`future_shuffle` must continue to receive the seventh frozen child stream, not the fourth.

Do not permit branch list order to redefine RNG child positions.

---

## 8. Protocol and condition expansion

### 8.1 Protocol

Represent the current protocol declaratively:

```text
T_sim = 800
burn_end_time = 160
split_time = 480
future_duration = 320
diagnostic_stride = 50
```

### 8.2 Condition expansion

Expand conditions deterministically in this exact nested order:

```text
for seed_index, seed in paired_seeds:
    for factor_level in declared level order:
```

For `T_window`, level order must be:

```python
(0.5, 0.75, 1.0, 1.5, 2.0)
```

Each condition needs:

```text
condition_id
seed
seed_index
factor level IDs and values
model config hash
protocol hash
expected branch set
```

Use a stable human-readable condition ID, e.g.:

```text
seed_11242426753702356865__rho_0p50
```

Retain exact numeric factor values in the manifest; do not infer values later from formatted IDs.

---

## 9. Collectors and output schema

### 9.1 Keep inference out of the runner

Collectors may save raw observables and deterministic condition-level summaries. They must not compute seed-level bootstrap intervals or inferential DIDs. Those remain in the analysis layer.

### 9.2 Core collector interface

```python
class Collector(Protocol):
    collector_id: str
    schema_version: str

    def validate_engine_result(...): ...
    def scalar_row(...): ...
    def array_payload(...): ...
```

### 9.3 `T_window` compatibility collector

Implement `TWindowLegacyCollectorV1` that preserves the current production data contract used by `AIEF_1_4_Twindow_sensitivity_analysis_v3.py`.

It must preserve:

- scalar column names;
- seed/rho/branch condition coverage;
- primary fixed-physical fields;
- secondary normalized-EMA fields;
- trajectory names;
- `B_final` names;
- prefix names;
- NPZ key format, including legacy rho formatting;
- condition status schema.

Do not change the current analysis script in this first modularization task.

### 9.4 Stable core schema versus extensions

Record in the manifest:

```text
core_schema_version
study_schema_version
collector IDs and versions
artifact naming policy ID
```

A future study may add namespaced fields without pretending that every study has an identical flat schema.

---

## 10. Output organization

Use a study-organized hierarchy:

```text
experiments/
    AIEF_1_4_S01_twindow_sensitivity/
        v1/
            <run_id>/
                baseline/
                    <execution_id>/
                        ... baseline artifacts ...
                production/
                    <execution_id>/
                        ... production artifacts ...
```

The leaf execution directory is the run directory passed to analysis.

### 10.1 Leaf directory layout

Preserve current root-level compatibility files for the `T_window` study:

```text
manifest.json
baseline_equivalence_certificate.json
baseline_equivalence_by_seed.json
twindow_condition_status.csv
AIEF_1_4_Twindow_sensitivity_<run_id>_scalar_summary.csv
AIEF_1_4_Twindow_sensitivity_<run_id>_branch_diagnostics.npz
```

Additional organization:

```text
conditions/
    condition_seed_<seed>_rho_<level>.npz
logs/
analysis/          # reserved for analysis driver
failure/           # optional structured failure diagnostics
```

Keep the consolidated CSV/NPZ at the leaf root so the existing analysis script can run unchanged.

### 10.2 Authority rules

- `manifest.json` is the execution authority.
- Consolidated CSV/NPZ are authoritative study outputs.
- Per-condition checkpoints are diagnostic and explicitly non-authoritative.
- `analysis/` is written only by the analysis layer.
- Optional catalogs are indexes, not authorities.

### 10.3 No mutable “latest” authority

Do not make a mutable `latest` symlink an authority. If created for convenience, mark it non-authoritative and rebuildable.

---

## 11. Rebuildable catalog

Implement a catalog command that scans leaf manifests and writes a catalog atomically.

Suggested output:

```text
experiments/catalog.csv
experiments/catalog.json
```

Columns/fields:

```text
study_id
study_slug
study_version
run_id
full_spec_sha256
execution_id
execution_mode
created_utc
status
freezeable
engine_sha256
runner_sha256
seed_count
condition_count
path
```

Requirements:

- catalog is derived from manifests;
- never use catalog as run authority;
- deterministic sorting;
- detect duplicate `(study_id, version, run_id, execution_id)`;
- flag malformed or incomplete manifests;
- atomic write;
- no silent overwrites.

---

## 12. Runner lifecycle

Implement a generic runner with this lifecycle:

1. Load registered study.
2. Validate spec.
3. Compute source/plugin hashes.
4. Compute canonical spec hash and scientific run ID.
5. Allocate a new execution directory and lock it.
6. Write initial manifest atomically.
7. Validate frozen authority paths.
8. Run mandatory frozen-baseline gate.
9. Save baseline certificate atomically.
10. If mode is baseline-only, mark completed and exit before condition expansion.
11. Expand all conditions deterministically.
12. For each condition:
    - build a fresh model config;
    - enforce regeneration policy;
    - create branch RNGs from the full namespace;
    - simulate prefix fresh;
    - simulate declared branches;
    - validate prefix, branches, arrays, metadata, and required outcomes;
    - write condition checkpoint atomically;
    - update condition status atomically.
13. Consolidate scalar and array outputs.
14. Verify exact expected condition and row counts.
15. Hash final outputs.
16. Write final manifest with `freezeable` status.
17. Release the execution lock.
18. Exit nonzero on any incomplete/non-freezeable production execution.

### 12.1 Condition status durability

Unlike the current end-only status write, persist condition status after every successfully committed condition or at a documented small interval. Use atomic whole-file replacement.

Do not call this “resume support.” It is crash diagnostics only in v1.

### 12.2 Resume policy

Do not implement resume in modular platform v1. A safe resume system requires strict validation of every checkpoint against spec, engine, schema, and source hashes. Add a clear failure if `--resume` is requested.

### 12.3 Locking

Prevent two processes from writing the same execution directory. Use an atomic lock file or OS file lock. Record PID, host, and start time. Stale-lock handling must require explicit user action; do not silently steal locks.

---

## 13. Baseline gate

Every production execution must run the engine’s mandatory baseline gate. There is no `--skip-baseline` production option.

For `T_window`, require:

```text
40/40 frozen seeds
7/7 frozen branches
all frozen prefix arrays exact
all frozen matrices/trajectories exact
all 42 frozen scalar fields exact
all rho=1 extension identities exact
all horizon metadata exact
```

Store:

```text
frozen manifest file hash
frozen NPZ file hash
frozen scalar CSV file hash
frozen production source hash
engine source hash
runner source hash
study module source hash
certificate path
seed-level certificate path
```

A certificate is reusable only if all linked source, spec, authority, and environment constraints match exactly. Do not implement certificate reuse in v1; always rerun it.

---

## 14. Validation gates

Implement explicit validators rather than message-string heuristics.

Suggested exceptions:

```python
class SpecValidationError(Exception): ...
class BaselineGateError(Exception): ...
class ConditionSchemaError(Exception): ...
class ArtifactIntegrityError(Exception): ...
class UnsupportedPolicyError(Exception): ...
```

Do not decide fatality by searching exception text for words like `schema` or `missing`.

Required condition checks for `T_window`:

- prefix keys, shape, dtype, and finiteness;
- all required branch keys;
- all 12x12 matrix shapes and finiteness;
- exact 640-point sample-time schedule;
- density finite and in `[0,1]`;
- similarity finite entries in `[-1,1]`, permitting NaN zero-vector cosine;
- exact `rho` and `T_window` metadata;
- exact `window_steps`, `recovery_end_ema`, fixed horizons;
- finite primary and secondary outcomes;
- no output-key collisions;
- exact branch set;
- exact condition count and scalar-row count.

---

## 15. Atomic artifacts and failure handling

All JSON, CSV, NPZ, and text writes must be atomic:

1. write temporary file in the destination directory;
2. flush;
3. `fsync` file;
4. atomic replace;
5. preferably `fsync` directory.

On failure:

- preserve already committed condition checkpoints;
- write `FAILED_manifest.json` or a final manifest with structured failure state;
- record exception type, message, condition ID, and traceback path;
- mark `freezeable=false`;
- exit nonzero;
- do not emit a misleading “completed” status.

Do not catch broad exceptions and continue after global spec/schema incompatibility.

---

## 16. CLI requirements

Implement subcommands rather than many loosely related flags.

### List

```bash
python AIEF_modular_driver_v1.py list-studies
```

### Describe

```bash
python AIEF_modular_driver_v1.py describe AIEF_1_4_S01
```

Print canonical study specification and expected counts.

### Dry run

```bash
python AIEF_modular_driver_v1.py dry-run AIEF_1_4_S01
```

Must not create a run directory. Validate:

- imports;
- registry;
- engine compatibility;
- factor levels;
- protocol;
- branch namespace;
- expected seeds/conditions/rows;
- canonical spec hash and run ID.

### Baseline only

```bash
python AIEF_modular_driver_v1.py baseline-only AIEF_1_4_S01 \
  --frozen-manifest ... \
  --frozen-npz ... \
  --frozen-scalar ... \
  --output-root experiments
```

### Production run

```bash
python AIEF_modular_driver_v1.py run AIEF_1_4_S01 \
  --frozen-manifest ... \
  --frozen-npz ... \
  --frozen-scalar ... \
  --output-root experiments
```

### Catalog

```bash
python AIEF_modular_driver_v1.py catalog \
  --output-root experiments
```

### Safety

- no production `--skip-baseline`;
- no default overwrite;
- `--overwrite` must require an exact leaf execution path and an additional confirmation flag, or omit overwrite entirely in v1;
- no resume in v1;
- deterministic nonzero exit codes.

---

## 17. `T_window` study specification

Register the first study as:

```text
study_id: AIEF_1_4_S01
study_slug: twindow_sensitivity
study_version: v1
```

Required model levels:

```python
rho = (0.5, 0.75, 1.0, 1.5, 2.0)
T_star = 25 / mean(omega)
T_window = rho * T_star
```

Required protocol:

```text
T_sim = 800
burn = 160
split = 480
future = 320
diagnostic stride = 50
```

Full RNG namespace:

```python
(
    "continue",
    "reset_ema",
    "reset_B",
    "reset_B_ema",
    "B_carrier_only",
    "full_reset",
    "future_shuffle",
)
```

Executed branches:

```python
(
    "continue",
    "reset_ema",
    "reset_B",
    "future_shuffle",
)
```

Expected production counts:

```text
40 seeds
5 rho levels
200 conditions
4 branches per condition
800 scalar rows
200 condition checkpoints
```

Primary and secondary execution outputs must remain compatible with the existing analysis driver.

---

## 18. Tests and staged acceptance

### 18.1 Static tests

- compile all new files;
- import all modules;
- list/describe study;
- canonical serialization deterministic across repeated calls;
- no duplicate registry IDs;
- run ID independent of output root and absolute source path;
- execution IDs differ between baseline and production modes;
- schema versions recorded.

### 18.2 Unit tests

- factor level expansion order;
- `rho -> T_window` exact mapping;
- full-regeneration policy enforcement;
- branch RNG child assignment, especially `future_shuffle` child index;
- exact seed generation;
- condition ID uniqueness;
- atomic file writes;
- failure manifest behavior;
- catalog rebuild and duplicate detection;
- unsupported policy failure.

### 18.3 One-condition smoke

Use one frozen seed and nonreference `rho=0.5`:

- fresh prefix;
- all four study branches;
- full RNG namespace;
- complete schema validation;
- checkpoint write/read round-trip;
- scalar extraction;
- array extraction.

### 18.4 Frozen baseline certification

Run complete 40-seed, seven-branch baseline equivalence with the new runner. It must pass exactly.

### 18.5 Selected oracle comparisons

Before a full 200-condition rerun, compare modular outputs with `runs/b57562a8ee77` for:

- at least two seeds, including seed `4619122171158768524`;
- all five rho levels;
- all four study branches;
- all scalar fields;
- all required arrays;
- all condition metadata.

Use exact NaN-aware equality.

### 18.6 Full oracle equivalence

Before declaring the modular runner a replacement, run the complete 200-condition study and compare logical contents against `runs/b57562a8ee77`:

```text
200/200 condition keys
800/800 scalar rows
all required arrays exact
all metadata exact
all branch RNG assignments exact
```

This is a workflow reproducibility test, not an independent experiment.

---

## 19. Acceptance criteria

The task is complete only when all of the following are true:

1. Existing engine, driver, analysis, and successful run are unchanged.
2. The modular package imports cleanly.
3. Registry lists `AIEF_1_4_S01` deterministically.
4. Dry-run creates no output directory.
5. Scientific run ID is stable and portable.
6. Baseline and production executions cannot collide.
7. Output hierarchy is organized by study ID, slug, version, run ID, and execution mode.
8. Every production run has immutable source/spec/authority hashes.
9. Full branch RNG namespace is preserved.
10. Every rho level regenerates from initialization.
11. Baseline gate is mandatory.
12. Per-condition status is durable and exact.
13. Consolidated outputs remain compatible with the current analysis driver.
14. Catalog is rebuildable and non-authoritative.
15. One-condition smoke passes.
16. Full frozen baseline passes.
17. Selected oracle comparisons pass.
18. Full oracle equivalence passes before replacement status.

---

## 20. Prohibited shortcuts

Do not:

- mutate the current successful driver in place;
- modify engine v1;
- copy numerical step code into the runner;
- treat `T_window` as a split intervention;
- reuse split states across rho;
- shorten or reorder the frozen RNG namespace;
- use branch execution order as RNG child order;
- omit the complete baseline gate;
- create a broad generic plugin that silently changes dynamics;
- claim support for unsupported intervention/forcing types;
- conflate collectors with inferential analysis;
- use edges or branches as independent replicates;
- add a new seed cohort;
- implement unsafe resume;
- use absolute paths or timestamps in scientific run IDs;
- make a mutable catalog or `latest` symlink authoritative;
- compare compressed NPZ file hashes instead of logical array contents for oracle equivalence;
- call a partially completed run freezeable.

---

## 21. Required coding-agent report

When finished, report:

1. new files created;
2. existing files modified, which should be none unless explicitly authorized;
3. CLI examples;
4. package/module diagram;
5. canonical identity payload definition;
6. output directory specification;
7. study registry contents;
8. validation and failure model;
9. tests run and exact results;
10. one-condition smoke result;
11. baseline certificate result, if executed;
12. oracle-comparison result, if executed;
13. remaining unsupported features;
14. known limitations and next safe extension.

Do not report “production ready” unless the full acceptance criteria, including baseline and oracle equivalence, have passed.
