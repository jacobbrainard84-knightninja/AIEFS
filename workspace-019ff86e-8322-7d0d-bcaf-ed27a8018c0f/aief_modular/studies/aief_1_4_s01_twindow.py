"""Declarative AIEF-1.4 S01 T_window sensitivity specification."""

from __future__ import annotations

import importlib
from typing import Any

import numpy as np

from ..branches import FROZEN_ENGINE_V1_NAMESPACE
from ..registry import register_study
from ..spec import (
    ArtifactPolicySpec,
    BaselineGateSpec,
    BranchSpec,
    CollectorSpec,
    ExperimentSpec,
    FactorLevel,
    FrozenDict,
    ModelFactorSpec,
    ProtocolSpec,
    SeedDesignSpec,
    ValidatorSpec,
)
from ..validation import SpecValidationError


STUDY_ID = "AIEF_1_4_S01"
STUDY_SLUG = "twindow_sensitivity"
STUDY_VERSION = "v1"
STUDY_TITLE = "AIEF-1.4 T_window Sensitivity"
ENGINE_MODULE = "aief_experiment_engine_v1"
MASTER_SEED = 20260714
N_SEEDS = 40
RHO_LEVELS = (
    ("rho_0p50", "rho=0.5", 0.5),
    ("rho_0p75", "rho=0.75", 0.75),
    ("rho_1p00", "rho=1.0", 1.0),
    ("rho_1p50", "rho=1.5", 1.5),
    ("rho_2p00", "rho=2.0", 2.0),
)
EXECUTED_BRANCHES = ("continue", "reset_ema", "reset_B", "future_shuffle")


def generate_seed_set(master_seed: int = MASTER_SEED, count: int = N_SEEDS) -> tuple[int, ...]:
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ValueError("seed count must be a positive integer")
    children = np.random.SeedSequence(int(master_seed)).spawn(count)
    seeds = tuple(int(child.generate_state(1, dtype=np.uint64)[0]) for child in children)
    if len(set(seeds)) != len(seeds):
        raise RuntimeError("SeedSequence generated duplicate paired seeds")
    return seeds


def _load_engine() -> Any:
    try:
        return importlib.import_module(ENGINE_MODULE)
    except ModuleNotFoundError as exc:
        raise SpecValidationError(
            f"Required certified engine module {ENGINE_MODULE!r} is not available. "
            "Place the modular package in the authoritative AIEF project repository."
        ) from exc


def _validate_engine_contract(engine: Any) -> None:
    expected_scalars = {
        "FROZEN_N": 12,
        "FROZEN_DT": 0.01,
        "FROZEN_TAU": 0.5,
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
    }
    for name, expected in expected_scalars.items():
        observed = getattr(engine, name, None)
        if observed != expected:
            raise SpecValidationError(
                f"Engine contract mismatch for {name}: observed={observed!r}, expected={expected!r}"
            )
    expected_omega = np.array(
        [1.00, 1.02, 1.50, 2.00, 2.01, 1.01, 1.03, 1.51, 2.02, 2.00, 1.00, 1.04],
        dtype=float,
    )
    if not np.array_equal(np.asarray(engine.FROZEN_OMEGA), expected_omega):
        raise SpecValidationError("Engine frozen omega array does not match AIEF-1.4 authority")
    if tuple(engine.DEFAULT_PROTOCOL_CONFIG.branches) != FROZEN_ENGINE_V1_NAMESPACE:
        raise SpecValidationError("Engine default branch namespace does not match frozen authority")


def build_twindow_spec() -> ExperimentSpec:
    engine = _load_engine()
    _validate_engine_contract(engine)

    base_model = engine.DEFAULT_MODEL_CONFIG
    base_model.validate()
    seeds = generate_seed_set()
    levels = tuple(
        FactorLevel(
            level_id=level_id,
            label=label,
            value=rho,
            metadata=FrozenDict(
                {
                    "parameter": "T_window",
                    "formula": "rho * T_star",
                    "T_window": rho * float(base_model.T_star),
                }
            ),
        )
        for level_id, label, rho in RHO_LEVELS
    )

    branches = (
        BranchSpec("continue", "continue", "control", (), None, False),
        BranchSpec(
            "reset_ema",
            "reset_ema",
            "state_intervention",
            ("engine_v1.reset_ema",),
            None,
            False,
        ),
        BranchSpec(
            "reset_B",
            "reset_B",
            "state_intervention",
            ("engine_v1.reset_B",),
            None,
            False,
        ),
        BranchSpec(
            "future_shuffle",
            "future_shuffle",
            "dynamic_forcing",
            (),
            "engine_v1.future_shuffle",
            True,
        ),
    )

    return ExperimentSpec(
        study_id=STUDY_ID,
        study_slug=STUDY_SLUG,
        study_version=STUDY_VERSION,
        title=STUDY_TITLE,
        purpose=(
            "Paired sensitivity study varying T_window = rho * T_star while "
            "fully regenerating each seed/rho trajectory"
        ),
        engine_module=ENGINE_MODULE,
        base_model=base_model,
        model_axes=(
            ModelFactorSpec(
                name="rho",
                levels=levels,
                reference_level_id="rho_1p00",
                regeneration_policy="full_from_initialization",
                resolver_id="engine_v1.twindow_scale",
            ),
        ),
        protocol=ProtocolSpec(
            T_sim=800.0,
            burn_end_time=160.0,
            split_time=480.0,
            future_duration=320.0,
            diagnostic_stride=50,
        ),
        seed_design=SeedDesignSpec(
            master_seed=MASTER_SEED,
            count=N_SEEDS,
            paired_seeds=seeds,
            generation_rule="numpy.SeedSequence(master_seed).spawn(count); child.generate_state(1,uint64)[0]",
        ),
        branch_rng_namespace=FROZEN_ENGINE_V1_NAMESPACE,
        branches=branches,
        collectors=(
            CollectorSpec(
                collector_id="aief.twindow.legacy-flat",
                schema_version="v1",
                core_schema_version="aief-engine-v1-raw-v1",
                study_schema_version="aief-1.4-s01-twindow-v1",
                requires_continue=True,
                settings=FrozenDict({"legacy_rho_key_format": "str(float)"}),
            ),
        ),
        baseline_gate=BaselineGateSpec(
            required=True,
            expected_seed_count=N_SEEDS,
            expected_branch_namespace=FROZEN_ENGINE_V1_NAMESPACE,
            exact_arrays=True,
            exact_scalars=True,
            certificate_reuse=False,
        ),
        artifact_policy=ArtifactPolicySpec(
            policy_id="aief.twindow.legacy-root-v1",
            scalar_filename_prefix="AIEF_1_4_Twindow_sensitivity",
            array_filename_prefix="AIEF_1_4_Twindow_sensitivity",
            checkpoint_role="diagnostic_non_authoritative",
            expected_condition_count=N_SEEDS * len(levels),
            expected_scalar_row_count=N_SEEDS * len(levels) * len(branches),
        ),
        validators=(
            ValidatorSpec(
                validator_id="aief.twindow.condition-v1",
                schema_version="v1",
                settings=FrozenDict(
                    {
                        "expected_samples": 640,
                        "fixed_immediate_time": 17.5,
                        "fixed_recovery_time": 87.5,
                    }
                ),
            ),
        ),
    )


register_study(
    STUDY_ID,
    build_twindow_spec,
    slug=STUDY_SLUG,
    version=STUDY_VERSION,
    title=STUDY_TITLE,
    source_module=__name__,
)
