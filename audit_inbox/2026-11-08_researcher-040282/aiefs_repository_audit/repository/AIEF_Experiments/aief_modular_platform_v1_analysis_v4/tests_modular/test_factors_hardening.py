from __future__ import annotations

import dataclasses
from types import SimpleNamespace

import pytest

from aief_modular.factors import (
    expand_conditions,
    model_config_hash,
    model_for_condition,
    reference_model_config,
    reference_selections,
    resolve_model_config,
    validate_factor_compatibility,
    validate_model_axes_compatibility,
)
from aief_modular.spec import (
    DesignExpectationsSpec,
    FactorLevel,
    ModelFactorSpec,
    canonical_json,
)
from aief_modular.validation import SpecValidationError, UnsupportedPolicyError


def test_expansion_is_completely_deterministic(small_spec):
    first = expand_conditions(small_spec)
    second = expand_conditions(small_spec)
    assert first == second
    assert canonical_json(first) == canonical_json(second)
    assert first[0].condition_id == "seed_101__rho_0p50"
    assert first[2].seed == 202


def test_model_hashes_share_by_level_and_differ_between_levels(small_spec):
    conditions = expand_conditions(small_spec)
    for rho in (0.5, 1.0):
        hashes = {
            condition.model_config_hash
            for condition in conditions
            if condition.value("rho") == rho
        }
        assert len(hashes) == 1
    assert len({condition.model_config_hash for condition in conditions}) == 2


def test_reference_and_reconstruction_are_exact(small_spec):
    reference = reference_model_config(small_spec)
    assert reference.T_window == small_spec.base_model.T_star
    for condition in expand_conditions(small_spec):
        reconstructed = model_for_condition(small_spec, condition)
        assert model_config_hash(reconstructed) == condition.model_config_hash


def test_modular_v1_rejects_multiple_axes(small_spec):
    second_levels = (
        FactorLevel("rho2_0p50", "rho2=.5", 0.5, {"T_window": 12.5}),
        FactorLevel("rho2_1p00", "rho2=1", 1.0, {"T_window": 25.0}),
    )
    second_axis = ModelFactorSpec(
        "rho2",
        second_levels,
        "rho2_1p00",
        "full_from_initialization",
        "engine_v1.twindow_scale",
    )
    multi = dataclasses.replace(
        small_spec,
        model_axes=(small_spec.model_axes[0], second_axis),
        design=DesignExpectationsSpec(8, 16),
    )
    with pytest.raises(UnsupportedPolicyError, match="exactly one"):
        validate_model_axes_compatibility(multi)


def test_invalid_rho_and_regeneration_policies_fail(small_spec):
    axis = small_spec.model_axes[0]
    for value in (0.0, -1.0):
        level = FactorLevel(f"rho_{value!s}".replace("-", "m").replace(".", "p"), str(value), value)
        with pytest.raises(SpecValidationError, match="rho must be finite and positive"):
            resolve_model_config(small_spec.base_model, ((axis, level),))
    with pytest.raises(ValueError, match="finite numeric"):
        FactorLevel("rho_nan", "nan", float("nan"))
    with pytest.raises(ValueError, match="finite numeric"):
        FactorLevel("rho_inf", "inf", float("inf"))

    nonfull = dataclasses.replace(axis, regeneration_policy="reuse_split")
    with pytest.raises(UnsupportedPolicyError, match="regeneration policy"):
        validate_factor_compatibility(nonfull)


def test_invalid_tstar_and_incompatible_model_are_typed(small_spec):
    negative_tstar_model = dataclasses.replace(small_spec.base_model, omega=(-1.0,) * 12)
    with pytest.raises(SpecValidationError, match="T_star must be finite and positive"):
        resolve_model_config(
            negative_tstar_model,
            ((small_spec.model_axes[0], small_spec.model_axes[0].levels[0]),),
        )

    incompatible = SimpleNamespace(T_star=25.0)
    with pytest.raises(SpecValidationError, match="not a compatible ModelConfig dataclass"):
        resolve_model_config(
            incompatible,
            ((small_spec.model_axes[0], small_spec.model_axes[0].levels[0]),),
        )


def test_reference_and_condition_levels_are_defensively_validated(small_spec):
    bad_axis = dataclasses.replace(small_spec.model_axes[0], reference_level_id="rho_missing")
    fake_spec = SimpleNamespace(model_axes=(bad_axis,))
    with pytest.raises(SpecValidationError, match="found 0"):
        reference_selections(fake_spec)

    condition = expand_conditions(small_spec)[0]
    original_level = condition.factor_levels[0][1]
    modified_level = dataclasses.replace(original_level, metadata={"T_window": 999.0})
    modified_condition = dataclasses.replace(
        condition,
        factor_levels=(("rho", modified_level),),
    )
    with pytest.raises(SpecValidationError, match="undeclared or modified"):
        model_for_condition(small_spec, modified_condition)
