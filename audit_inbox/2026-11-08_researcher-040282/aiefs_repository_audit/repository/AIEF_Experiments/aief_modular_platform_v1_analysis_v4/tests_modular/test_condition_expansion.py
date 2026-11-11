from __future__ import annotations

from aief_modular.factors import expand_conditions, model_for_condition
from aief_modular.studies.aief_1_4_s01_twindow import generate_seed_set


def test_exact_frozen_seed_generation():
    seeds = generate_seed_set()
    assert len(seeds) == 40
    assert seeds[:3] == (
        11242426753702356865,
        4619122171158768524,
        16329425431442249417,
    )
    assert len(set(seeds)) == 40


def test_seed_major_factor_level_order(small_spec):
    conditions = expand_conditions(small_spec)
    assert [(item.seed, item.level("rho").level_id) for item in conditions] == [
        (101, "rho_0p50"),
        (101, "rho_1p00"),
        (202, "rho_0p50"),
        (202, "rho_1p00"),
    ]
    assert len({item.condition_id for item in conditions}) == 4


def test_rho_to_twindow_exact_mapping(small_spec):
    conditions = expand_conditions(small_spec)
    model_half = model_for_condition(small_spec, conditions[0])
    model_one = model_for_condition(small_spec, conditions[1])
    assert model_half.T_window == 0.5 * small_spec.base_model.T_star
    assert model_one.T_window == small_spec.base_model.T_star
    assert model_half is not small_spec.base_model
