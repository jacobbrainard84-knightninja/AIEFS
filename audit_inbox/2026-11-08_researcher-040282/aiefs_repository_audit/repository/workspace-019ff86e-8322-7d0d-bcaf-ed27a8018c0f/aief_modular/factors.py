"""Typed model-factor resolution and deterministic condition expansion."""

from __future__ import annotations

import dataclasses
import hashlib
import importlib
import itertools
import math
from dataclasses import dataclass
from typing import Any

from .spec import ExperimentSpec, FactorLevel, ModelFactorSpec, canonical_json, sha256_canonical
from .validation import SpecValidationError, UnsupportedPolicyError


SUPPORTED_RESOLVERS = frozenset({"engine_v1.twindow_scale"})
SUPPORTED_REGENERATION_POLICY = "full_from_initialization"


@dataclass(frozen=True)
class Condition:
    condition_id: str
    seed: int
    seed_index: int
    factor_levels: tuple[tuple[str, FactorLevel], ...]
    factor_values: tuple[tuple[str, float], ...]
    model_config_hash: str
    protocol_hash: str
    expected_branches: tuple[str, ...]

    def level(self, factor_name: str) -> FactorLevel:
        for name, level in self.factor_levels:
            if name == factor_name:
                return level
        raise KeyError(factor_name)

    def value(self, factor_name: str) -> float:
        return self.level(factor_name).value


def validate_factor_compatibility(axis: ModelFactorSpec) -> None:
    if axis.regeneration_policy != SUPPORTED_REGENERATION_POLICY:
        raise UnsupportedPolicyError(
            f"Factor {axis.name!r} requests unsupported regeneration policy "
            f"{axis.regeneration_policy!r}"
        )
    if axis.resolver_id not in SUPPORTED_RESOLVERS:
        raise UnsupportedPolicyError(
            f"Factor resolver {axis.resolver_id!r} is not implemented by modular platform v1"
        )


def resolve_model_config(base_model: Any, selections: tuple[tuple[ModelFactorSpec, FactorLevel], ...]) -> Any:
    """Create a fresh immutable engine ModelConfig for selected factor levels."""
    model = base_model
    for axis, level in selections:
        validate_factor_compatibility(axis)
        if axis.resolver_id == "engine_v1.twindow_scale":
            rho = float(level.value)
            if not math.isfinite(rho) or rho <= 0.0:
                raise SpecValidationError(f"rho must be finite and positive, got {rho!r}")
            try:
                t_star = float(model.T_star)
            except Exception as exc:
                raise SpecValidationError("Base model does not expose finite T_star") from exc
            t_window = rho * t_star
            model = dataclasses.replace(model, T_window=t_window)
        else:  # defensive: validate_factor_compatibility should already reject it
            raise UnsupportedPolicyError(axis.resolver_id)

    if model is base_model and selections:
        raise RuntimeError("Factor resolver failed to create a fresh model configuration")
    validate = getattr(model, "validate", None)
    if not callable(validate):
        raise SpecValidationError("Resolved model config has no validate() method")
    validate()
    return model


def reference_selections(spec: ExperimentSpec) -> tuple[tuple[ModelFactorSpec, FactorLevel], ...]:
    selected: list[tuple[ModelFactorSpec, FactorLevel]] = []
    for axis in spec.model_axes:
        selected.append(
            (
                axis,
                next(level for level in axis.levels if level.level_id == axis.reference_level_id),
            )
        )
    return tuple(selected)


def reference_model_config(spec: ExperimentSpec) -> Any:
    return resolve_model_config(spec.base_model, reference_selections(spec))


def model_config_hash(model: Any) -> str:
    return sha256_canonical(model)


def protocol_hash(spec: ExperimentSpec) -> str:
    return sha256_canonical(spec.protocol)


def _condition_id(seed: int, selections: tuple[tuple[ModelFactorSpec, FactorLevel], ...]) -> str:
    suffix = "__".join(level.level_id for _axis, level in selections)
    return f"seed_{seed}__{suffix}" if suffix else f"seed_{seed}"


def expand_conditions(spec: ExperimentSpec) -> tuple[Condition, ...]:
    """Expand in exact seed-major, declared-factor-level order."""
    for axis in spec.model_axes:
        validate_factor_compatibility(axis)

    level_products = tuple(itertools.product(*(axis.levels for axis in spec.model_axes)))
    conditions: list[Condition] = []
    seen_ids: set[str] = set()
    p_hash = protocol_hash(spec)
    expected_branches = tuple(branch.engine_branch for branch in spec.branches)

    for seed_index, seed in enumerate(spec.seed_design.paired_seeds):
        for level_tuple in level_products:
            selections = tuple(zip(spec.model_axes, level_tuple, strict=True))
            model = resolve_model_config(spec.base_model, selections)
            condition_id = _condition_id(seed, selections)
            if condition_id in seen_ids:
                raise SpecValidationError(f"Duplicate condition ID: {condition_id}")
            seen_ids.add(condition_id)
            conditions.append(
                Condition(
                    condition_id=condition_id,
                    seed=int(seed),
                    seed_index=seed_index,
                    factor_levels=tuple((axis.name, level) for axis, level in selections),
                    factor_values=tuple((axis.name, float(level.value)) for axis, level in selections),
                    model_config_hash=model_config_hash(model),
                    protocol_hash=p_hash,
                    expected_branches=expected_branches,
                )
            )

    if len(conditions) != spec.artifact_policy.expected_condition_count:
        raise SpecValidationError(
            f"Expanded {len(conditions)} conditions, expected "
            f"{spec.artifact_policy.expected_condition_count}"
        )
    return tuple(conditions)


def selections_for_condition(
    spec: ExperimentSpec,
    condition: Condition,
) -> tuple[tuple[ModelFactorSpec, FactorLevel], ...]:
    by_name = dict(condition.factor_levels)
    return tuple((axis, by_name[axis.name]) for axis in spec.model_axes)


def model_for_condition(spec: ExperimentSpec, condition: Condition) -> Any:
    model = resolve_model_config(spec.base_model, selections_for_condition(spec, condition))
    observed = model_config_hash(model)
    if observed != condition.model_config_hash:
        raise SpecValidationError(
            f"Condition {condition.condition_id} model hash changed: "
            f"expanded={condition.model_config_hash}, resolved={observed}"
        )
    return model
