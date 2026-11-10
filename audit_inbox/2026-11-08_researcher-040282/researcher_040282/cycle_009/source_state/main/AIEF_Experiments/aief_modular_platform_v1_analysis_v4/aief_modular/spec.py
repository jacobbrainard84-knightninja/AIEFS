"""Immutable experiment specifications and canonical scientific identities.

The specification layer deliberately contains no execution code.  It describes
only scientific design, engine compatibility, schemas, and artifact policy.
Runtime provenance (paths, timestamps, hosts, and execution mode) is kept out
of canonical scientific identities.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any


JsonScalar = str | int | float | bool | None


class FrozenDict(Mapping[str, Any]):
    """Small immutable, deterministically ordered mapping.

    Values are recursively frozen.  This is used instead of mutable dictionaries
    inside frozen specification dataclasses.
    """

    __slots__ = ("_items", "_dict")

    def __init__(self, values: Mapping[str, Any] | None = None):
        source = {} if values is None else values
        items: list[tuple[str, Any]] = []
        for key, value in source.items():
            if not isinstance(key, str):
                raise TypeError(
                    f"FrozenDict key must be str, got {type(key).__name__}"
                )
            items.append((key, freeze_value(value)))
        items.sort(key=lambda item: item[0])
        if len({key for key, _value in items}) != len(items):
            raise TypeError("FrozenDict source contains duplicate string keys")
        self._items = tuple(items)
        self._dict = dict(self._items)

    def __getitem__(self, key: str) -> Any:
        return self._dict[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    def __hash__(self) -> int:
        return hash(self._items)

    def __repr__(self) -> str:
        return f"FrozenDict({dict(self._items)!r})"


def freeze_value(value: Any) -> Any:
    """Recursively convert JSON-like containers to immutable containers."""
    if isinstance(value, FrozenDict):
        return value
    if isinstance(value, Mapping):
        return FrozenDict(value)
    if isinstance(value, (list, tuple)):
        return tuple(freeze_value(item) for item in value)
    if isinstance(value, (set, frozenset)):
        raise TypeError("Sets are not permitted in immutable canonical specifications")
    return value


@dataclass(frozen=True)
class FactorLevel:
    level_id: str
    label: str
    value: float
    metadata: Mapping[str, Any] = field(default_factory=FrozenDict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", FrozenDict(self.metadata))
        if not self.level_id or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", self.level_id):
            raise ValueError(f"Invalid factor level ID: {self.level_id!r}")
        if not self.label:
            raise ValueError("Factor level label must be nonempty")
        if isinstance(self.value, bool) or not math.isfinite(float(self.value)):
            raise ValueError(f"Factor level {self.level_id!r} must have a finite numeric value")


@dataclass(frozen=True)
class ModelFactorSpec:
    name: str
    levels: tuple[FactorLevel, ...]
    reference_level_id: str
    regeneration_policy: str
    resolver_id: str


@dataclass(frozen=True)
class ProtocolSpec:
    T_sim: float
    burn_end_time: float
    split_time: float
    future_duration: float
    diagnostic_stride: int


@dataclass(frozen=True)
class SeedDesignSpec:
    master_seed: int
    count: int
    paired_seeds: tuple[int, ...]
    generation_rule: str


@dataclass(frozen=True)
class BranchSpec:
    name: str
    engine_branch: str
    role: str
    intervention_ids: tuple[str, ...] = ()
    forcing_policy_id: str | None = None
    requires_rng: bool = False


@dataclass(frozen=True)
class CollectorSpec:
    collector_id: str
    schema_version: str
    core_schema_version: str
    study_schema_version: str
    requires_continue: bool = False
    settings: Mapping[str, Any] = field(default_factory=FrozenDict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "settings", FrozenDict(self.settings))


@dataclass(frozen=True)
class BaselineGateSpec:
    required: bool
    expected_seed_count: int
    expected_branch_namespace: tuple[str, ...]
    authority_id: str
    exact_arrays: bool = True
    exact_scalars: bool = True
    certificate_reuse: bool = False


@dataclass(frozen=True)
class DesignExpectationsSpec:
    expected_condition_count: int
    expected_scalar_row_count: int


@dataclass(frozen=True)
class ArtifactPolicySpec:
    policy_id: str
    scalar_filename_prefix: str
    array_filename_prefix: str
    checkpoint_role: str
    manifest_filename: str = "manifest.json"
    failed_manifest_filename: str = "FAILED_manifest.json"
    baseline_certificate_filename: str = "baseline_equivalence_certificate.json"
    baseline_by_seed_filename: str = "baseline_equivalence_by_seed.json"
    condition_status_filename: str = "condition_status.csv"
    lock_filename: str = ".execution.lock"


@dataclass(frozen=True)
class ValidatorSpec:
    validator_id: str
    schema_version: str
    settings: Mapping[str, Any] = field(default_factory=FrozenDict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "settings", FrozenDict(self.settings))


@dataclass(frozen=True)
class ExperimentSpec:
    study_id: str
    study_slug: str
    study_version: str
    title: str
    purpose: str
    engine_module: str
    base_model: Any
    model_axes: tuple[ModelFactorSpec, ...]
    protocol: ProtocolSpec
    design: DesignExpectationsSpec
    seed_design: SeedDesignSpec
    branch_rng_namespace: tuple[str, ...]
    branches: tuple[BranchSpec, ...]
    collectors: tuple[CollectorSpec, ...]
    baseline_gate: BaselineGateSpec
    artifact_policy: ArtifactPolicySpec
    validators: tuple[ValidatorSpec, ...]
    study_metadata: Mapping[str, Any] = field(default_factory=FrozenDict)
    analysis_contract: Mapping[str, Any] = field(default_factory=FrozenDict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "study_metadata", FrozenDict(self.study_metadata))
        object.__setattr__(self, "analysis_contract", FrozenDict(self.analysis_contract))
        validate_experiment_spec(self)


class CanonicalizationError(ValueError):
    """Raised when an object cannot enter a canonical scientific identity."""


def _canonical_value(value: Any) -> Any:
    """Convert supported objects into canonical JSON-compatible values."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            item.name: _canonical_value(getattr(value, item.name))
            for item in dataclasses.fields(value)
        }
    if isinstance(value, Mapping):
        converted: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError(f"Canonical mapping key must be str, got {type(key).__name__}")
            converted[key] = _canonical_value(item)
        return converted
    if isinstance(value, (tuple, list)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, bool) or value is None or isinstance(value, (str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CanonicalizationError("NaN and Infinity are forbidden in canonical JSON")
        return value

    # NumPy is optional at this layer.  Handle scalar objects without making it
    # a package import requirement.
    item_method = getattr(value, "item", None)
    if callable(item_method):
        scalar = item_method()
        if scalar is not value:
            return _canonical_value(scalar)

    raise CanonicalizationError(
        f"Unsupported canonical value {type(value).__module__}.{type(value).__qualname__}"
    )


def canonical_data(value: Any) -> Any:
    """Return the JSON-compatible canonical data tree for ``value``."""
    return _canonical_value(value)


def canonical_json(value: Any) -> str:
    """Serialize with stable ordering and full round-trip float precision."""
    return json.dumps(
        canonical_data(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def spec_sha256(spec: ExperimentSpec) -> str:
    return sha256_canonical(spec)


def scientific_identity_payload(
    spec: ExperimentSpec,
    source_hashes: Mapping[str, str],
) -> dict[str, Any]:
    """Build the complete, path-free scientific identity payload.

    Some fields are intentionally repeated outside the canonical specification.
    This makes audit records explicit and guards against a future spec serializer
    accidentally omitting a scientifically material field.
    """
    axis_levels = {
        axis.name: [
            {
                "level_id": level.level_id,
                "value": level.value,
                "metadata": level.metadata,
            }
            for level in axis.levels
        ]
        for axis in spec.model_axes
    }
    return {
        "identity_schema": "aief-scientific-run-identity-v1",
        "study_id": spec.study_id,
        "study_version": spec.study_version,
        "canonical_spec": canonical_data(spec),
        "spec_sha256": spec_sha256(spec),
        "source_hashes": dict(sorted(source_hashes.items())),
        "paired_seeds": list(spec.seed_design.paired_seeds),
        "seed_generation_rule": spec.seed_design.generation_rule,
        "model_factor_levels": axis_levels,
        "protocol": canonical_data(spec.protocol),
        "branch_rng_namespace": list(spec.branch_rng_namespace),
        "executed_branches": [branch.engine_branch for branch in spec.branches],
        "collectors": [
            {
                "collector_id": collector.collector_id,
                "schema_version": collector.schema_version,
                "core_schema_version": collector.core_schema_version,
                "study_schema_version": collector.study_schema_version,
            }
            for collector in spec.collectors
        ],
    }


def scientific_run_sha256(spec: ExperimentSpec, source_hashes: Mapping[str, str]) -> str:
    return sha256_canonical(scientific_identity_payload(spec, source_hashes))


SAFE_COMPONENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SAFE_FILENAME_RE = re.compile(r"^\.?[A-Za-z0-9][A-Za-z0-9._-]*$")


def validate_safe_component(value: str, label: str, *, filename: bool = False) -> None:
    """Reject traversal, separators, controls, whitespace, and empty components."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a nonempty string")
    expression = SAFE_FILENAME_RE if filename else SAFE_COMPONENT_RE
    if not expression.fullmatch(value) or value in {".", ".."}:
        raise ValueError(f"Unsafe {label}: {value!r}")


def _duplicates(values: list[str] | tuple[str, ...]) -> list[str]:
    return sorted({value for value in values if values.count(value) > 1})


def validate_experiment_spec(spec: ExperimentSpec) -> None:
    """Validate static scientific and orchestration invariants."""
    validate_safe_component(spec.study_id, "study_id")
    validate_safe_component(spec.study_slug, "study_slug")
    validate_safe_component(spec.study_version, "study_version")
    if not spec.title or not spec.purpose:
        raise ValueError("title and purpose must be nonempty")
    validate_safe_component(spec.engine_module, "engine_module")

    factor_names = [axis.name for axis in spec.model_axes]
    if len(factor_names) != len(set(factor_names)):
        raise ValueError(f"Duplicate factor names: {_duplicates(factor_names)}")
    for axis in spec.model_axes:
        validate_safe_component(axis.name, "factor name")
        validate_safe_component(axis.reference_level_id, "reference level ID")
        if not axis.levels:
            raise ValueError(f"Factor {axis.name!r} has no levels")
        ids = [level.level_id for level in axis.levels]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Factor {axis.name!r} has duplicate level IDs: {_duplicates(ids)}")
        for level_id in ids:
            if not level_id.startswith(f"{axis.name}_"):
                raise ValueError(
                    f"Factor level ID {level_id!r} must include axis prefix {axis.name + '_'!r}"
                )
        if axis.reference_level_id not in ids:
            raise ValueError(
                f"Factor {axis.name!r} reference level {axis.reference_level_id!r} is absent"
            )
        if axis.regeneration_policy != "full_from_initialization":
            raise ValueError(
                f"Unsupported regeneration policy {axis.regeneration_policy!r}; "
                "engine-v1 modular studies require full_from_initialization"
            )

    protocol = spec.protocol
    times = (
        protocol.T_sim,
        protocol.burn_end_time,
        protocol.split_time,
        protocol.future_duration,
    )
    if any(isinstance(value, bool) or not math.isfinite(float(value)) for value in times):
        raise ValueError("Protocol times must be finite numbers")
    if not (0.0 < protocol.burn_end_time < protocol.split_time < protocol.T_sim):
        raise ValueError("Protocol must satisfy 0 < burn < split < T_sim")
    if protocol.future_duration <= 0.0:
        raise ValueError("future_duration must be positive")
    if protocol.split_time + protocol.future_duration != protocol.T_sim:
        raise ValueError("split_time + future_duration must equal T_sim exactly")
    if isinstance(protocol.diagnostic_stride, bool) or not isinstance(protocol.diagnostic_stride, int):
        raise ValueError("diagnostic_stride must be a positive integer")
    if protocol.diagnostic_stride <= 0:
        raise ValueError("diagnostic_stride must be positive")

    seeds = spec.seed_design
    if isinstance(seeds.master_seed, bool) or not isinstance(seeds.master_seed, int):
        raise ValueError("master_seed must be an integer")
    if seeds.count <= 0 or len(seeds.paired_seeds) != seeds.count:
        raise ValueError("Seed count does not match paired seed list")
    if len(set(seeds.paired_seeds)) != seeds.count:
        raise ValueError("Paired seed list contains duplicates")
    if not seeds.generation_rule:
        raise ValueError("seed generation rule must be recorded")

    namespace = spec.branch_rng_namespace
    if not namespace or len(namespace) != len(set(namespace)):
        raise ValueError("branch_rng_namespace must be nonempty and unique")
    branch_names = [branch.name for branch in spec.branches]
    engine_names = [branch.engine_branch for branch in spec.branches]
    for branch_name in branch_names:
        validate_safe_component(branch_name, "branch name")
    for engine_name in engine_names:
        validate_safe_component(engine_name, "engine branch name")
    if len(branch_names) != len(set(branch_names)):
        raise ValueError(f"Duplicate branch names: {_duplicates(branch_names)}")
    if len(engine_names) != len(set(engine_names)):
        raise ValueError(f"Duplicate executed engine branches: {_duplicates(engine_names)}")
    unknown = set(engine_names) - set(namespace)
    if unknown:
        raise ValueError(f"Executed branches outside RNG namespace: {sorted(unknown)}")

    collector_names = [collector.collector_id for collector in spec.collectors]
    if not collector_names or len(collector_names) != len(set(collector_names)):
        raise ValueError("Collector IDs must be nonempty and unique")
    for collector in spec.collectors:
        validate_safe_component(collector.collector_id, "collector ID")
        validate_safe_component(collector.schema_version, "collector schema version")
        validate_safe_component(collector.core_schema_version, "core schema version")
        validate_safe_component(collector.study_schema_version, "study schema version")
    if any(collector.requires_continue for collector in spec.collectors) and "continue" not in engine_names:
        raise ValueError("At least one collector requires the continue branch")

    validator_names = [validator.validator_id for validator in spec.validators]
    if len(validator_names) != len(set(validator_names)):
        raise ValueError(f"Duplicate validator IDs: {_duplicates(validator_names)}")
    for validator in spec.validators:
        validate_safe_component(validator.validator_id, "validator ID")
        validate_safe_component(validator.schema_version, "validator schema version")

    gate = spec.baseline_gate
    if gate.required:
        validate_safe_component(gate.authority_id, "baseline authority ID")
        if gate.expected_seed_count != seeds.count:
            raise ValueError("Baseline gate seed count differs from seed design")
        if gate.expected_branch_namespace != namespace:
            raise ValueError("Baseline gate branch namespace differs from RNG namespace")
        if gate.certificate_reuse:
            raise ValueError("Certificate reuse is unsupported in modular platform v1")

    policy = spec.artifact_policy
    validate_safe_component(policy.policy_id, "artifact policy ID")
    validate_safe_component(policy.scalar_filename_prefix, "scalar filename prefix")
    validate_safe_component(policy.array_filename_prefix, "array filename prefix")
    validate_safe_component(policy.checkpoint_role, "checkpoint role")
    for label, filename in (
        ("manifest filename", policy.manifest_filename),
        ("failed manifest filename", policy.failed_manifest_filename),
        ("baseline certificate filename", policy.baseline_certificate_filename),
        ("baseline-by-seed filename", policy.baseline_by_seed_filename),
        ("condition status filename", policy.condition_status_filename),
        ("lock filename", policy.lock_filename),
    ):
        validate_safe_component(filename, label, filename=True)
    filenames = (
        policy.manifest_filename,
        policy.failed_manifest_filename,
        policy.baseline_certificate_filename,
        policy.baseline_by_seed_filename,
        policy.condition_status_filename,
        policy.lock_filename,
    )
    if len(filenames) != len(set(filenames)):
        raise ValueError("Artifact policy filenames must be unique")
    if policy.manifest_filename != "manifest.json":
        raise ValueError(
            "Modular platform v1 catalogs require manifest_filename='manifest.json'"
        )
    if spec.design.expected_condition_count <= 0:
        raise ValueError("Expected condition count must be positive")
    if spec.design.expected_scalar_row_count <= 0:
        raise ValueError("Expected scalar row count must be positive")
    derived_condition_count = spec.seed_design.count * math.prod(
        len(axis.levels) for axis in spec.model_axes
    )
    if spec.design.expected_condition_count != derived_condition_count:
        raise ValueError(
            f"Prespecified condition count {spec.design.expected_condition_count} "
            f"!= derived count {derived_condition_count}"
        )
    derived_scalar_rows = derived_condition_count * len(spec.branches)
    if spec.design.expected_scalar_row_count != derived_scalar_rows:
        raise ValueError(
            f"Prespecified scalar row count {spec.design.expected_scalar_row_count} "
            f"!= derived count {derived_scalar_rows}"
        )

    # Verify that canonical serialization succeeds at construction time.
    canonical_json(spec)
