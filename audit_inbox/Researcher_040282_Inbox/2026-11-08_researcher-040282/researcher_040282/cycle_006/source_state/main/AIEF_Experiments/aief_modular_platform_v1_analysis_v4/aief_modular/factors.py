"""Typed model-factor resolution and deterministic condition expansion."""

from __future__ import annotations

import dataclasses
import itertools
import math
from dataclasses import dataclass
from typing import Any

from .spec import ExperimentSpec, FactorLevel, ModelFactorSpec, sha256_canonical
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
    model_metadata: tuple[tuple[str, float | int], ...]
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


def validate_model_axes_compatibility(spec: ExperimentSpec) -> ModelFactorSpec:
    """Modular platform v1 supports exactly the single certified rho axis."""
    if len(spec.model_axes) != 1:
        raise UnsupportedPolicyError(
            "Modular platform v1 supports exactly one model axis"
        )
    axis = spec.model_axes[0]
    if axis.name != "rho":
        raise UnsupportedPolicyError(
            f"Modular platform v1 requires factor name 'rho', got {axis.name!r}"
        )
    validate_factor_compatibility(axis)
    if axis.resolver_id != "engine_v1.twindow_scale":
        raise UnsupportedPolicyError(
            f"Modular platform v1 requires the T_window resolver, got {axis.resolver_id!r}"
        )
    return axis


def resolve_model_config(base_model: Any, selections: tuple[tuple[ModelFactorSpec, FactorLevel], ...]) -> Any:
    """Create a fresh immutable engine ModelConfig for the one supported level."""
    if len(selections) != 1:
        raise UnsupportedPolicyError(
            "Modular platform v1 resolves exactly one rho factor selection"
        )
    model = base_model
    for axis, level in selections:
        if axis.name != "rho":
            raise UnsupportedPolicyError(
                f"Modular platform v1 requires factor name 'rho', got {axis.name!r}"
            )
        validate_factor_compatibility(axis)
        if axis.resolver_id == "engine_v1.twindow_scale":
            rho = float(level.value)
            if not math.isfinite(rho) or rho <= 0.0:
                raise SpecValidationError(f"rho must be finite and positive, got {rho!r}")
            try:
                t_star = float(model.T_star)
            except Exception as exc:
                raise SpecValidationError("Base model does not expose numeric T_star") from exc
            if not math.isfinite(t_star) or t_star <= 0.0:
                raise SpecValidationError(
                    f"Base model T_star must be finite and positive, got {t_star!r}"
                )
            t_window = rho * t_star
            if not math.isfinite(t_window) or t_window <= 0.0:
                raise SpecValidationError(
                    f"Resolved T_window must be finite and positive, got {t_window!r}"
                )
            try:
                model = dataclasses.replace(model, T_window=t_window)
            except TypeError as exc:
                raise SpecValidationError(
                    "Base model is not a compatible ModelConfig dataclass"
                ) from exc
        else:  # defensive: validate_factor_compatibility should already reject it
            raise UnsupportedPolicyError(axis.resolver_id)

    if model is base_model and selections:
        raise RuntimeError("Factor resolver failed to create a fresh model configuration")
    validate = getattr(model, "validate", None)
    if not callable(validate):
        raise SpecValidationError("Resolved model config has no validate() method")
    try:
        validate()
    except Exception as exc:
        raise SpecValidationError(f"Resolved model config failed validation: {exc}") from exc
    return model


def reference_selections(spec: ExperimentSpec) -> tuple[tuple[ModelFactorSpec, FactorLevel], ...]:
    validate_model_axes_compatibility(spec)
    selected: list[tuple[ModelFactorSpec, FactorLevel]] = []
    for axis in spec.model_axes:
        matches = [
            level for level in axis.levels
            if level.level_id == axis.reference_level_id
        ]
        if len(matches) != 1:
            raise SpecValidationError(
                f"Factor {axis.name!r} requires exactly one reference level "
                f"{axis.reference_level_id!r}; found {len(matches)}"
            )
        selected.append((axis, matches[0]))
    return tuple(selected)


def reference_model_config(spec: ExperimentSpec) -> Any:
    return resolve_model_config(spec.base_model, reference_selections(spec))


def model_config_hash(model: Any) -> str:
    return sha256_canonical(model)


def protocol_hash(spec: ExperimentSpec) -> str:
    return sha256_canonical(spec.protocol)


def _condition_id(seed: int, selections: tuple[tuple[ModelFactorSpec, FactorLevel], ...]) -> str:
    encoded_levels: list[str] = []
    for axis, level in selections:
        if not level.level_id.startswith(f"{axis.name}_"):
            raise SpecValidationError(
                f"Level ID {level.level_id!r} does not encode factor {axis.name!r}"
            )
        # Level IDs include the factor prefix by specification, so S01 retains
        # the required human-readable form seed_<seed>__rho_0p50.
        encoded_levels.append(level.level_id)
    suffix = "__".join(encoded_levels)
    return f"seed_{seed}__{suffix}"


def expand_conditions(spec: ExperimentSpec) -> tuple[Condition, ...]:
    """Expand in exact seed-major, declared-factor-level order."""
    validate_model_axes_compatibility(spec)

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
            window_steps = int(round(float(model.T_window) / float(model.dt)))
            t_window_effective = window_steps * float(model.dt)
            recovery_end_steps = min(
                5 * window_steps,
                int(round(spec.protocol.future_duration / float(model.dt))),
            )
            conditions.append(
                Condition(
                    condition_id=condition_id,
                    seed=int(seed),
                    seed_index=seed_index,
                    factor_levels=tuple((axis.name, level) for axis, level in selections),
                    factor_values=tuple((axis.name, float(level.value)) for axis, level in selections),
                    model_metadata=(
                        ("T_window_nominal", float(model.T_window)),
                        ("window_steps", window_steps),
                        ("T_window_effective", t_window_effective),
                        ("T_window_rounding_error", t_window_effective - float(model.T_window)),
                        ("recovery_end_steps", recovery_end_steps),
                    ),
                    model_config_hash=model_config_hash(model),
                    protocol_hash=p_hash,
                    expected_branches=expected_branches,
                )
            )

    if len(conditions) != spec.design.expected_condition_count:
        raise SpecValidationError(
            f"Expanded {len(conditions)} conditions, expected "
            f"{spec.design.expected_condition_count}"
        )
    return tuple(conditions)


def selections_for_condition(
    spec: ExperimentSpec,
    condition: Condition,
) -> tuple[tuple[ModelFactorSpec, FactorLevel], ...]:
    validate_model_axes_compatibility(spec)
    if len(condition.factor_levels) != len(spec.model_axes):
        raise SpecValidationError(
            f"Condition {condition.condition_id} has {len(condition.factor_levels)} factor levels; "
            f"expected {len(spec.model_axes)}"
        )
    names = [name for name, _level in condition.factor_levels]
    if len(names) != len(set(names)):
        raise SpecValidationError(
            f"Condition {condition.condition_id} has duplicate factor names"
        )
    by_name = dict(condition.factor_levels)
    selections: list[tuple[ModelFactorSpec, FactorLevel]] = []
    for axis in spec.model_axes:
        condition_level = by_name.get(axis.name)
        if condition_level is None:
            raise SpecValidationError(
                f"Condition {condition.condition_id} is missing factor {axis.name!r}"
            )
        declared = {level.level_id: level for level in axis.levels}
        expected = declared.get(condition_level.level_id)
        if expected is None or condition_level != expected:
            raise SpecValidationError(
                f"Condition {condition.condition_id} uses undeclared or modified level "
                f"{condition_level!r} for factor {axis.name!r}"
            )
        selections.append((axis, expected))
    extra_names = set(names) - {axis.name for axis in spec.model_axes}
    if extra_names:
        raise SpecValidationError(
            f"Condition {condition.condition_id} has undeclared factors {sorted(extra_names)}"
        )
    return tuple(selections)


def model_for_condition(spec: ExperimentSpec, condition: Condition) -> Any:
    selections = selections_for_condition(spec, condition)
    if not (0 <= condition.seed_index < len(spec.seed_design.paired_seeds)):
        raise SpecValidationError(
            f"Condition {condition.condition_id} has invalid seed_index {condition.seed_index}"
        )
    expected_seed = spec.seed_design.paired_seeds[condition.seed_index]
    if condition.seed != expected_seed:
        raise SpecValidationError(
            f"Condition {condition.condition_id} seed {condition.seed} != {expected_seed}"
        )
    expected_id = _condition_id(condition.seed, selections)
    if condition.condition_id != expected_id:
        raise SpecValidationError(
            f"Condition ID {condition.condition_id!r} != canonical {expected_id!r}"
        )
    expected_values = tuple(
        (axis.name, float(level.value)) for axis, level in selections
    )
    if condition.factor_values != expected_values:
        raise SpecValidationError(
            f"Condition {condition.condition_id} factor values differ from declared levels"
        )
    if condition.protocol_hash != protocol_hash(spec):
        raise SpecValidationError(
            f"Condition {condition.condition_id} protocol hash differs from specification"
        )
    expected_branches = tuple(branch.engine_branch for branch in spec.branches)
    if condition.expected_branches != expected_branches:
        raise SpecValidationError(
            f"Condition {condition.condition_id} branch set/order differs from specification"
        )

    model = resolve_model_config(spec.base_model, selections)
    observed = model_config_hash(model)
    if observed != condition.model_config_hash:
        raise SpecValidationError(
            f"Condition {condition.condition_id} model hash changed: "
            f"expanded={condition.model_config_hash}, resolved={observed}"
        )
    return model
