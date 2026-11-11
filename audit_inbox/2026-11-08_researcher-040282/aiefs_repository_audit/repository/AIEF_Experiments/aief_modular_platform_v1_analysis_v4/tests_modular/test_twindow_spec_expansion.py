from __future__ import annotations

import dataclasses
import sys
from types import SimpleNamespace

import numpy as np

from aief_modular.branches import FROZEN_ENGINE_V1_NAMESPACE
from aief_modular.factors import expand_conditions, model_config_hash, model_for_condition, reference_model_config
from aief_modular.studies import aief_1_4_s01_twindow as study


def _fake_certified_engine(base_model):
    omega = np.array(
        [1.00, 1.02, 1.50, 2.00, 2.01, 1.01, 1.03, 1.51, 2.02, 2.00, 1.00, 1.04],
        dtype=float,
    )
    model = dataclasses.replace(
        base_model,
        omega=tuple(omega.tolist()),
        T_window=25.0 / float(np.mean(omega)),
    )
    values = {
        "FROZEN_N": 12,
        "FROZEN_DT": 0.01,
        "FROZEN_TAU": 0.5,
        "FROZEN_OMEGA": omega,
        "FROZEN_A": 1.0,
        "FROZEN_Q": 1.5,
        "FROZEN_DELTA": 0.05,
        "FROZEN_ETA": 0.04,
        "FROZEN_MU": 0.03,
        "FROZEN_GAMMA": 0.015,
        "FROZEN_B_C": 0.12,
        "FROZEN_B_INIT_SCALE": 0.0005,
        "FROZEN_ZERO_TOL": 1e-12,
        "FROZEN_T_SIM": 800.0,
        "FROZEN_BURN_END": 16000,
        "FROZEN_HIST_END": 48000,
        "FROZEN_FUTURE_STEPS": 32000,
        "FROZEN_DELAY_STEPS": 50,
        "FROZEN_WINDOW_STEPS": 1750,
        "FROZEN_RECOVERY_END": 8750,
        "DEFAULT_MODEL_CONFIG": model,
        "DEFAULT_PROTOCOL_CONFIG": SimpleNamespace(branches=FROZEN_ENGINE_V1_NAMESPACE),
    }
    return SimpleNamespace(**values)


def test_full_s01_expansion_contract(monkeypatch, small_spec):
    fake_engine = _fake_certified_engine(small_spec.base_model)
    monkeypatch.setitem(sys.modules, study.ENGINE_MODULE, fake_engine)
    spec = study.build_twindow_spec()
    conditions = expand_conditions(spec)

    assert len(conditions) == 200
    assert [condition.value("rho") for condition in conditions[:5]] == [
        0.5, 0.75, 1.0, 1.5, 2.0
    ]
    assert conditions[0].seed == spec.seed_design.paired_seeds[0]
    assert conditions[0].condition_id == (
        f"seed_{spec.seed_design.paired_seeds[0]}__rho_0p50"
    )
    assert conditions[5].seed == spec.seed_design.paired_seeds[1]

    for rho in (0.5, 0.75, 1.0, 1.5, 2.0):
        hashes = {
            condition.model_config_hash
            for condition in conditions
            if condition.value("rho") == rho
        }
        assert len(hashes) == 1
    assert len({condition.model_config_hash for condition in conditions}) == 5

    reference = reference_model_config(spec)
    assert reference.T_window == spec.base_model.T_star
    for condition in conditions:
        reconstructed = model_for_condition(spec, condition)
        assert model_config_hash(reconstructed) == condition.model_config_hash

    assert expand_conditions(spec) == conditions
