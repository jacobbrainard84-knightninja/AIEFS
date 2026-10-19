from __future__ import annotations

import math
from dataclasses import dataclass

import pytest

from aief_modular.branches import FROZEN_ENGINE_V1_NAMESPACE
from aief_modular.spec import (
    ArtifactPolicySpec,
    BaselineGateSpec,
    BranchSpec,
    CollectorSpec,
    ExperimentSpec,
    FactorLevel,
    ModelFactorSpec,
    ProtocolSpec,
    SeedDesignSpec,
    ValidatorSpec,
)


@dataclass(frozen=True)
class FakeModel:
    N: int = 12
    dt: float = 0.01
    tau: float = 0.5
    omega: tuple[float, ...] = (1.0,) * 12
    a: float = 1.0
    q: float = 1.5
    delta: float = 0.05
    eta: float = 0.04
    mu: float = 0.03
    gamma: float = 0.015
    T_window: float = 25.0
    B_c: float = 0.12
    B_init_scale: float = 0.0005
    scale_epsilon: float = 1e-12

    @property
    def mean_omega(self):
        return sum(self.omega) / len(self.omega)

    @property
    def T_star(self):
        return 25.0 / self.mean_omega

    @property
    def alpha(self):
        return math.exp(-self.dt / self.T_window)

    @property
    def delay_steps(self):
        return round(self.tau / self.dt)

    def validate(self):
        if self.T_window <= 0:
            raise ValueError("T_window")


@pytest.fixture
def small_spec():
    levels = (
        FactorLevel("rho_0p50", "rho=.5", 0.5, {"T_window": 12.5}),
        FactorLevel("rho_1p00", "rho=1", 1.0, {"T_window": 25.0}),
    )
    return ExperimentSpec(
        study_id="TEST_S01",
        study_slug="test_study",
        study_version="v1",
        title="Test study",
        purpose="Unit testing",
        engine_module="fake_engine",
        base_model=FakeModel(),
        model_axes=(
            ModelFactorSpec(
                "rho", levels, "rho_1p00", "full_from_initialization", "engine_v1.twindow_scale"
            ),
        ),
        protocol=ProtocolSpec(800.0, 160.0, 480.0, 320.0, 50),
        seed_design=SeedDesignSpec(7, 2, (101, 202), "test generation"),
        branch_rng_namespace=FROZEN_ENGINE_V1_NAMESPACE,
        branches=(
            BranchSpec("continue", "continue", "control"),
            BranchSpec(
                "future_shuffle",
                "future_shuffle",
                "dynamic_forcing",
                (),
                "engine_v1.future_shuffle",
                True,
            ),
        ),
        collectors=(
            CollectorSpec(
                "aief.twindow.legacy-flat",
                "v1",
                "aief-engine-v1-raw-v1",
                "aief-1.4-s01-twindow-v1",
                True,
            ),
        ),
        baseline_gate=BaselineGateSpec(True, 2, FROZEN_ENGINE_V1_NAMESPACE),
        artifact_policy=ArtifactPolicySpec(
            "test-policy", "study", "study", "diagnostic_non_authoritative", 4, 8
        ),
        validators=(ValidatorSpec("test-validator", "v1"),),
    )
