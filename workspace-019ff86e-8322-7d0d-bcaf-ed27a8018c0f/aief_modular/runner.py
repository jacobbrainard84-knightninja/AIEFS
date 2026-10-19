"""Generic modular experiment runner for certified engine-v1 studies."""

from __future__ import annotations

import importlib
import json
import os
import platform
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from .artifacts import (
    ExecutionLock,
    ExecutionPaths,
    atomic_write_csv,
    atomic_write_json,
    atomic_write_npz,
    atomic_write_text,
    create_execution_directory,
    execution_paths,
    file_sha256,
    make_execution_id,
    utc_now_text,
)
from .branches import branch_rng_child_index, make_branch_rngs, validate_branch_compatibility
from .collectors import TWindowLegacyCollectorV1, build_collector
from .factors import (
    Condition,
    expand_conditions,
    model_for_condition,
    reference_model_config,
    validate_factor_compatibility,
)
from .registry import StudyRegistration
from .spec import (
    ExperimentSpec,
    canonical_data,
    canonical_json,
    scientific_identity_payload,
    scientific_run_sha256,
    spec_sha256,
    validate_experiment_spec,
)
from .validation import (
    ArtifactIntegrityError,
    BaselineGateError,
    ConditionSchemaError,
    SpecValidationError,
    UnsupportedPolicyError,
)


RUNNER_VERSION = "v1.0"
RUN_ID_LENGTH = 16


def _module_source_hash(module: Any) -> str:
    path_value = getattr(module, "__file__", None)
    if not path_value:
        raise ArtifactIntegrityError(f"Module {module.__name__!r} has no source file")
    path = Path(path_value)
    if path.suffix == ".pyc" and path.with_suffix(".py").exists():
        path = path.with_suffix(".py")
    return file_sha256(path)


def compute_source_hashes(
    spec: ExperimentSpec,
    registration: StudyRegistration,
    engine: Any,
) -> dict[str, str]:
    """Hash all execution and plugin sources under stable logical names."""
    modules = {
        "engine": engine,
        "runner": importlib.import_module("aief_modular.runner"),
        "spec": importlib.import_module("aief_modular.spec"),
        "registry": importlib.import_module("aief_modular.registry"),
        "factors": importlib.import_module("aief_modular.factors"),
        "branches": importlib.import_module("aief_modular.branches"),
        "collectors": importlib.import_module("aief_modular.collectors"),
        "validation": importlib.import_module("aief_modular.validation"),
        "artifacts": importlib.import_module("aief_modular.artifacts"),
        "study": importlib.import_module(registration.source_module),
    }
    cli_path = Path(__file__).resolve().parent.parent / "AIEF_modular_driver_v1.py"
    hashes = {name: _module_source_hash(module) for name, module in modules.items()}
    if not cli_path.is_file():
        raise ArtifactIntegrityError(f"CLI source not found: {cli_path.name}")
    hashes["cli"] = file_sha256(cli_path)
    return dict(sorted(hashes.items()))


def build_engine_protocol(engine: Any, spec: ExperimentSpec, branches: tuple[str, ...]) -> Any:
    protocol = engine.ProtocolConfig(
        T_sim=spec.protocol.T_sim,
        burn_end_time=spec.protocol.burn_end_time,
        split_time=spec.protocol.split_time,
        future_duration=spec.protocol.future_duration,
        diagnostic_stride=spec.protocol.diagnostic_stride,
        branches=tuple(branches),
    )
    return protocol


def validate_engine_compatibility(engine: Any, spec: ExperimentSpec) -> None:
    validate_experiment_spec(spec)
    validate_branch_compatibility(spec)
    for axis in spec.model_axes:
        validate_factor_compatibility(axis)
    required_api = (
        "ModelConfig",
        "ProtocolConfig",
        "simulate_prefix",
        "simulate_future",
        "make_branch_rngs",
        "run_baseline_equivalence",
        "REQUIRED_BRANCH_MATRIX_KEYS",
    )
    missing = [name for name in required_api if not hasattr(engine, name)]
    if missing:
        raise UnsupportedPolicyError(f"Engine module missing required API: {missing}")

    reference = reference_model_config(spec)
    reference.validate()
    protocol = build_engine_protocol(
        engine,
        spec,
        tuple(branch.engine_branch for branch in spec.branches),
    )
    protocol.validate(reference)


def dry_run(registration: StudyRegistration) -> dict[str, Any]:
    """Validate and compute identities without creating an output directory."""
    spec = registration.build()
    engine = importlib.import_module(spec.engine_module)
    validate_engine_compatibility(engine, spec)
    source_hashes = compute_source_hashes(spec, registration, engine)
    conditions = expand_conditions(spec)
    identity_sha = scientific_run_sha256(spec, source_hashes)
    return {
        "status": "validated",
        "study_id": spec.study_id,
        "study_slug": spec.study_slug,
        "study_version": spec.study_version,
        "spec_sha256": spec_sha256(spec),
        "scientific_identity_sha256": identity_sha,
        "run_id": identity_sha[:RUN_ID_LENGTH],
        "seed_count": spec.seed_design.count,
        "condition_count": len(conditions),
        "scalar_row_count": spec.artifact_policy.expected_scalar_row_count,
        "branch_rng_namespace": list(spec.branch_rng_namespace),
        "executed_branches": [branch.engine_branch for branch in spec.branches],
        "future_shuffle_rng_child_index": branch_rng_child_index(spec, "future_shuffle"),
        "collector_schemas": [
            {
                "collector_id": item.collector_id,
                "schema_version": item.schema_version,
                "core_schema_version": item.core_schema_version,
                "study_schema_version": item.study_schema_version,
            }
            for item in spec.collectors
        ],
        "source_hashes": source_hashes,
    }


def _model_manifest(spec: ExperimentSpec) -> dict[str, Any]:
    model = spec.base_model
    return {
        "N": int(model.N),
        "dt": float(model.dt),
        "tau": float(model.tau),
        "omega": [float(value) for value in model.omega],
        "a": float(model.a),
        "q": float(model.q),
        "delta": float(model.delta),
        "eta": float(model.eta),
        "mu": float(model.mu),
        "gamma": float(model.gamma),
        "B_c": float(model.B_c),
        "B_init_scale": float(model.B_init_scale),
        "T_star": float(model.T_star),
        "scale_epsilon": float(model.scale_epsilon),
    }


def _initial_manifest(
    *,
    spec: ExperimentSpec,
    spec_hash: str,
    scientific_hash: str,
    run_id: str,
    execution_id: str,
    execution_mode: str,
    source_hashes: Mapping[str, str],
    paths: ExecutionPaths,
) -> dict[str, Any]:
    rho_axis = next(axis for axis in spec.model_axes if axis.name == "rho")
    rho_values = [float(level.value) for level in rho_axis.levels]
    twindow_values = [float(level.metadata["T_window"]) for level in rho_axis.levels]
    collector = spec.collectors[0]
    return {
        "manifest_schema": "aief-modular-execution-manifest-v1",
        "runner_version": RUNNER_VERSION,
        "study_id": spec.study_id,
        "study_slug": spec.study_slug,
        "study_version": spec.study_version,
        "study_name": "AIEF_1_4_Twindow_sensitivity",
        "title": spec.title,
        "purpose": spec.purpose,
        "spec_sha256": spec_hash,
        "scientific_identity_sha256": scientific_hash,
        "run_id": run_id,
        "execution_id": execution_id,
        "execution_mode": execution_mode,
        "created_utc": utc_now_text(),
        "execution_provenance": {
            "pid": os.getpid(),
            "host": platform.node(),
            "started_utc": utc_now_text(),
        },
        "status": "initialized",
        "freezeable": False,
        "source_hashes": dict(source_hashes),
        "canonical_spec": canonical_data(spec),
        "scientific_identity_payload": scientific_identity_payload(spec, source_hashes),
        "model": _model_manifest(spec),
        "protocol": {
            "T_sim": spec.protocol.T_sim,
            "burn_end_time": spec.protocol.burn_end_time,
            "split_time": spec.protocol.split_time,
            "future_duration": spec.protocol.future_duration,
            "diagnostic_stride": spec.protocol.diagnostic_stride,
            "branches": [branch.engine_branch for branch in spec.branches],
        },
        "study": {
            "rho_values": rho_values,
            "T_window_values": twindow_values,
            "n_seeds": spec.seed_design.count,
            "statistical_unit": "paired seed/graph",
            "expected_condition_count": spec.artifact_policy.expected_condition_count,
            "expected_scalar_row_count": spec.artifact_policy.expected_scalar_row_count,
        },
        "randomization": {
            "master_seed": spec.seed_design.master_seed,
            "paired_seeds": list(spec.seed_design.paired_seeds),
            "seed_generation": spec.seed_design.generation_rule,
            "branch_rng_namespace": list(spec.branch_rng_namespace),
            "executed_branches": [branch.engine_branch for branch in spec.branches],
            "branch_rng_child_indices": {
                branch.engine_branch: branch_rng_child_index(spec, branch.engine_branch)
                for branch in spec.branches
            },
            "bit_generator": np.random.default_rng(0).bit_generator.__class__.__name__,
        },
        "schema": {
            "core_schema_version": collector.core_schema_version,
            "study_schema_version": collector.study_schema_version,
            "collectors": [
                {
                    "collector_id": item.collector_id,
                    "schema_version": item.schema_version,
                    "core_schema_version": item.core_schema_version,
                    "study_schema_version": item.study_schema_version,
                }
                for item in spec.collectors
            ],
            "artifact_naming_policy_id": spec.artifact_policy.policy_id,
        },
        "artifact_authority": {
            "manifest": "execution_authority",
            "consolidated_csv": "authoritative_study_output",
            "consolidated_npz": "authoritative_study_output",
            "condition_checkpoints": spec.artifact_policy.checkpoint_role,
            "catalog": "derived_non_authoritative",
            "analysis_directory": "analysis_layer_only",
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "artifacts": {
            "scalar_csv": paths.scalar_csv.name,
            "branch_npz": paths.branch_npz.name,
            "condition_status": paths.condition_status.name,
            "conditions_directory": paths.conditions.name,
        },
    }


def _validate_authority_paths(
    frozen_manifest: str | Path,
    frozen_npz: str | Path,
    frozen_scalar: str | Path,
) -> dict[str, Path]:
    paths = {
        "manifest": Path(frozen_manifest),
        "npz": Path(frozen_npz),
        "scalar": Path(frozen_scalar),
    }
    for label, path in paths.items():
        if not path.is_file():
            raise ArtifactIntegrityError(f"Frozen {label} authority not found: {path}")
    return paths


def _run_baseline_gate(
    *,
    engine: Any,
    spec: ExperimentSpec,
    authority: Mapping[str, Path],
) -> dict[str, Any]:
    reference_model = reference_model_config(spec)
    baseline_protocol = build_engine_protocol(engine, spec, tuple(spec.branch_rng_namespace))
    reference_model.validate()
    baseline_protocol.validate(reference_model)
    return engine.run_baseline_equivalence(
        seeds=list(spec.seed_design.paired_seeds),
        config=reference_model,
        protocol=baseline_protocol,
        frozen_manifest_path=str(authority["manifest"]),
        frozen_npz_path=str(authority["npz"]),
        frozen_csv_path=str(authority["scalar"]),
        branch_order=tuple(spec.branch_rng_namespace),
    )


def _validate_baseline_result(result: Mapping[str, Any], spec: ExperimentSpec) -> None:
    if result.get("status") != "passed":
        raise BaselineGateError(
            f"Mandatory frozen baseline gate failed: {result.get('error', 'per-seed mismatch')}"
        )
    if int(result.get("n_seeds", -1)) != spec.baseline_gate.expected_seed_count:
        raise BaselineGateError("Baseline result seed count is incorrect")
    seed_results = result.get("seed_results", {})
    if set(seed_results) != {str(seed) for seed in spec.seed_design.paired_seeds}:
        raise BaselineGateError("Baseline certificate seed cohort is incomplete")
    if any(item.get("status") != "passed" for item in seed_results.values()):
        raise BaselineGateError("At least one baseline seed is not certified")


def _write_condition_status(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    failed = any(row.get("status") == "failed" for row in rows)
    fields = ("seed", "rho", "status", "elapsed_seconds", "error") if failed else (
        "seed",
        "rho",
        "status",
        "elapsed_seconds",
    )
    normalized = []
    for row in rows:
        normalized.append({field: row.get(field, "") for field in fields})
    atomic_write_csv(path, normalized, fields)


def _simulate_condition(
    *,
    engine: Any,
    spec: ExperimentSpec,
    condition: Condition,
    collector: TWindowLegacyCollectorV1,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    # A new ModelConfig and a new prefix are created for every condition.  There
    # is intentionally no split-state cache in modular platform v1.
    model = model_for_condition(spec, condition)
    protocol = build_engine_protocol(
        engine,
        spec,
        tuple(branch.engine_branch for branch in spec.branches),
    )
    model.validate()
    protocol.validate(model)

    split_state, prefix = engine.simulate_prefix(condition.seed, model, protocol)
    rngs = make_branch_rngs(engine, condition.seed, tuple(spec.branch_rng_namespace))
    branch_results: dict[str, dict[str, Any]] = {}
    rho = float(condition.value("rho"))
    for branch_spec in spec.branches:
        branch = branch_spec.engine_branch
        result = engine.simulate_future(
            split_state.clone(),
            prefix,
            branch,
            model,
            protocol,
            rngs[branch],
        )
        result["T_window"] = model.T_window
        result["rho"] = rho
        branch_results[branch] = result

    collector.validate_engine_result(
        engine=engine,
        condition=condition,
        model=model,
        protocol=protocol,
        prefix=prefix,
        branch_results=branch_results,
    )
    rows = collector.scalar_rows(condition=condition, branch_results=branch_results)
    payload = collector.array_payload(
        condition=condition,
        model=model,
        prefix=prefix,
        branch_results=branch_results,
    )
    return rows, payload


def execute(
    registration: StudyRegistration,
    *,
    mode: str,
    frozen_manifest: str | Path,
    frozen_npz: str | Path,
    frozen_scalar: str | Path,
    output_root: str | Path,
    resume: bool = False,
) -> ExecutionPaths:
    """Run baseline-only or complete production execution."""
    if resume:
        raise UnsupportedPolicyError(
            "Resume is not implemented in modular platform v1; checkpoints are crash diagnostics only"
        )
    if mode not in {"baseline", "production"}:
        raise ValueError(f"Unsupported execution mode: {mode}")

    spec = registration.build()
    engine = importlib.import_module(spec.engine_module)
    validate_engine_compatibility(engine, spec)
    source_hashes = compute_source_hashes(spec, registration, engine)
    full_spec_hash = spec_sha256(spec)
    scientific_hash = scientific_run_sha256(spec, source_hashes)
    run_id = scientific_hash[:RUN_ID_LENGTH]
    execution_id = make_execution_id(mode)
    paths = execution_paths(output_root, spec, run_id, mode, execution_id)
    create_execution_directory(paths)

    manifest = _initial_manifest(
        spec=spec,
        spec_hash=full_spec_hash,
        scientific_hash=scientific_hash,
        run_id=run_id,
        execution_id=execution_id,
        execution_mode=mode,
        source_hashes=source_hashes,
        paths=paths,
    )
    atomic_write_json(paths.manifest, manifest)

    current_condition: Condition | None = None
    status_rows: list[dict[str, Any]] = []
    started = time.time()

    try:
        with ExecutionLock(paths.lock_file):
            authority = _validate_authority_paths(frozen_manifest, frozen_npz, frozen_scalar)
            manifest["frozen_authority"] = {
                "manifest_file_sha256": file_sha256(authority["manifest"]),
                "npz_file_sha256": file_sha256(authority["npz"]),
                "scalar_csv_file_sha256": file_sha256(authority["scalar"]),
            }
            try:
                with open(authority["manifest"], "r", encoding="utf-8") as handle:
                    frozen_data = json.load(handle)
                manifest["frozen_authority"]["production_source_sha256"] = frozen_data.get(
                    "source_sha256", "NOT_RECORDED"
                )
            except Exception as exc:
                raise ArtifactIntegrityError(f"Cannot read frozen manifest: {exc}") from exc
            atomic_write_json(paths.manifest, manifest)

            baseline = _run_baseline_gate(engine=engine, spec=spec, authority=authority)
            # Persist both passing and failing baseline diagnostics before the
            # gate is interpreted. A failed certificate is never reusable.
            atomic_write_json(paths.baseline_certificate, baseline)
            atomic_write_json(paths.baseline_by_seed, baseline.get("seed_results", {}))
            _validate_baseline_result(baseline, spec)
            manifest["baseline_equivalence"] = {
                "status": "passed",
                "n_seeds_tested": baseline["n_seeds"],
                "n_seeds_passed": baseline["n_seeds"],
                "branches_validated": list(spec.branch_rng_namespace),
                "certificate_path": paths.baseline_certificate.name,
                "seed_results_path": paths.baseline_by_seed.name,
                "certificate_sha256": file_sha256(paths.baseline_certificate),
                "seed_results_sha256": file_sha256(paths.baseline_by_seed),
                "engine_source_sha256": source_hashes["engine"],
                "runner_source_sha256": source_hashes["runner"],
                "study_source_sha256": source_hashes["study"],
            }
            atomic_write_json(paths.manifest, manifest)

            if mode == "baseline":
                manifest.update(
                    {
                        "status": "baseline_only_completed",
                        "freezeable": False,
                        "completion": {
                            "status": "baseline_only_completed",
                            "study_grid_started": False,
                            "baseline_passed": True,
                            "elapsed_seconds": time.time() - started,
                        },
                        "output_hashes": {
                            "baseline_certificate": file_sha256(paths.baseline_certificate),
                            "baseline_seed_results": file_sha256(paths.baseline_by_seed),
                        },
                    }
                )
                atomic_write_json(paths.manifest, manifest)
                return paths

            conditions = expand_conditions(spec)
            manifest["conditions"] = [
                {
                    "condition_id": condition.condition_id,
                    "seed": condition.seed,
                    "seed_index": condition.seed_index,
                    "factor_levels": {
                        factor_name: {
                            "level_id": level.level_id,
                            "label": level.label,
                            "value": level.value,
                            "metadata": dict(level.metadata),
                        }
                        for factor_name, level in condition.factor_levels
                    },
                    "factor_values": dict(condition.factor_values),
                    "model_config_hash": condition.model_config_hash,
                    "protocol_hash": condition.protocol_hash,
                    "expected_branches": list(condition.expected_branches),
                }
                for condition in conditions
            ]
            atomic_write_json(paths.manifest, manifest)

            collector_spec = spec.collectors[0]
            collector = build_collector(collector_spec)
            if not isinstance(collector, TWindowLegacyCollectorV1):
                raise UnsupportedPolicyError("Only TWindowLegacyCollectorV1 is supported in v1")

            all_rows: list[dict[str, Any]] = []
            consolidated_payload: dict[str, Any] = {}
            successful = 0

            for current_condition in conditions:
                condition_started = time.time()
                try:
                    condition_rows, condition_payload = _simulate_condition(
                        engine=engine,
                        spec=spec,
                        condition=current_condition,
                        collector=collector,
                    )
                    overlap = set(consolidated_payload) & set(condition_payload)
                    if overlap:
                        raise ConditionSchemaError(
                            f"Consolidated NPZ key collision: {sorted(overlap)[:10]}"
                        )
                    checkpoint = paths.conditions / collector.checkpoint_filename(current_condition)
                    atomic_write_npz(checkpoint, condition_payload)

                    # Commit in-memory consolidation only after checkpoint success.
                    all_rows.extend(condition_rows)
                    consolidated_payload.update(condition_payload)
                    status_rows.append(
                        {
                            "seed": current_condition.seed,
                            "rho": current_condition.value("rho"),
                            "status": "success",
                            "elapsed_seconds": time.time() - condition_started,
                        }
                    )
                    _write_condition_status(paths.condition_status, status_rows)
                    successful += 1
                except Exception as exc:
                    status_rows.append(
                        {
                            "seed": current_condition.seed,
                            "rho": current_condition.value("rho"),
                            "status": "failed",
                            "elapsed_seconds": time.time() - condition_started,
                            "error": f"{type(exc).__name__}: {exc}",
                        }
                    )
                    _write_condition_status(paths.condition_status, status_rows)
                    raise

            expected_conditions = spec.artifact_policy.expected_condition_count
            expected_rows = spec.artifact_policy.expected_scalar_row_count
            if successful != expected_conditions:
                raise ArtifactIntegrityError(
                    f"Successful condition count {successful} != {expected_conditions}"
                )
            if len(all_rows) != expected_rows:
                raise ArtifactIntegrityError(f"Scalar row count {len(all_rows)} != {expected_rows}")
            checkpoint_count = len(list(paths.conditions.glob("condition_seed_*_rho_*.npz")))
            if checkpoint_count != expected_conditions:
                raise ArtifactIntegrityError(
                    f"Checkpoint count {checkpoint_count} != {expected_conditions}"
                )

            all_rows.sort(key=lambda row: (int(row["seed_index"]), float(row["rho"]), str(row["branch"])))
            atomic_write_csv(paths.scalar_csv, all_rows, collector.scalar_fieldnames())
            atomic_write_npz(paths.branch_npz, consolidated_payload)

            output_hashes = {
                "scalar_csv": file_sha256(paths.scalar_csv),
                "branch_npz": file_sha256(paths.branch_npz),
                "condition_status_csv": file_sha256(paths.condition_status),
                "baseline_certificate": file_sha256(paths.baseline_certificate),
                "baseline_seed_results": file_sha256(paths.baseline_by_seed),
            }
            manifest.update(
                {
                    "status": "completed",
                    "freezeable": True,
                    "condition_status": {
                        "path": paths.condition_status.name,
                        "sha256": output_hashes["condition_status_csv"],
                        "expected_rows": expected_conditions,
                        "successful_rows": successful,
                        "failed_rows": 0,
                    },
                    "checkpoints": {
                        "role": spec.artifact_policy.checkpoint_role,
                        "count": checkpoint_count,
                        "authoritative_consolidation": paths.branch_npz.name,
                    },
                    "completion": {
                        "status": "completed",
                        "n_conditions_requested": expected_conditions,
                        "n_conditions_successful": successful,
                        "n_conditions_failed": 0,
                        "n_scalar_rows": len(all_rows),
                        "n_matrix_entries": len(consolidated_payload),
                        "elapsed_seconds": time.time() - started,
                        "freezeable": True,
                    },
                    "output_hashes": output_hashes,
                }
            )
            atomic_write_json(paths.manifest, manifest)
            return paths

    except Exception as exc:
        trace_path = paths.failure / "traceback.txt"
        atomic_write_text(trace_path, traceback.format_exc())
        failure_artifacts: dict[str, Any] = {}
        if paths.baseline_certificate.exists():
            failure_artifacts["baseline_certificate"] = {
                "path": paths.baseline_certificate.name,
                "sha256": file_sha256(paths.baseline_certificate),
            }
        if paths.condition_status.exists():
            failure_artifacts["condition_status"] = {
                "path": paths.condition_status.name,
                "sha256": file_sha256(paths.condition_status),
            }
        failure = {
            "status": "failed",
            "freezeable": False,
            "failure": {
                "exception_type": type(exc).__name__,
                "message": str(exc),
                "condition_id": current_condition.condition_id if current_condition else None,
                "traceback_path": str(trace_path.relative_to(paths.leaf)),
                "elapsed_seconds": time.time() - started,
                "committed_condition_rows": len(status_rows),
                "diagnostic_artifacts": failure_artifacts,
            },
        }
        manifest.update(failure)
        atomic_write_json(paths.manifest, manifest)
        atomic_write_json(paths.failed_manifest, manifest)
        raise
