from __future__ import annotations

from dataclasses import dataclass

from aief_modular.factors import expand_conditions
from aief_modular.runner import _simulate_condition


@dataclass
class FakeState:
    token: int

    def clone(self):
        return FakeState(self.token)


class FakeProtocol:
    def __init__(
        self,
        T_sim,
        burn_end_time,
        split_time,
        future_duration,
        diagnostic_stride,
        branches,
    ):
        self.T_sim = T_sim
        self.burn_end_time = burn_end_time
        self.split_time = split_time
        self.future_duration = future_duration
        self.diagnostic_stride = diagnostic_stride
        self.branches = branches

    def validate(self, model):
        return None

    def future_steps(self, model):
        return round(self.future_duration / model.dt)


class FakeEngine:
    ProtocolConfig = FakeProtocol
    prefix_calls = []
    future_calls = []

    @classmethod
    def reset(cls):
        cls.prefix_calls = []
        cls.future_calls = []

    @classmethod
    def simulate_prefix(cls, seed, model, protocol):
        token = len(cls.prefix_calls) + 1
        cls.prefix_calls.append((token, seed, model.T_window))
        return FakeState(token), {"prefix_token": token}

    @staticmethod
    def make_branch_rngs(seed, namespace):
        return {branch: object() for branch in namespace}

    @classmethod
    def simulate_future(cls, split_state, prefix, branch, model, protocol, rng):
        cls.future_calls.append(
            (split_state.token, prefix["prefix_token"], branch, model.T_window)
        )
        return {}


class RecordingCollector:
    def validate_engine_result(self, **kwargs):
        return None

    def scalar_rows(self, *, condition, branch_results):
        return [
            {"seed": condition.seed, "branch": branch}
            for branch in branch_results
        ]

    def array_payload(self, *, condition, model, prefix, branch_results):
        return {f"condition_{condition.condition_id}": prefix["prefix_token"]}


def test_every_condition_regenerates_prefix_from_initialization(small_spec):
    FakeEngine.reset()
    conditions = expand_conditions(small_spec)
    collector = RecordingCollector()

    for condition in conditions:
        _simulate_condition(
            engine=FakeEngine,
            spec=small_spec,
            condition=condition,
            collector=collector,
        )

    assert len(FakeEngine.prefix_calls) == len(conditions) == 4
    assert [token for token, _seed, _twindow in FakeEngine.prefix_calls] == [1, 2, 3, 4]
    assert [(seed, twindow) for _token, seed, twindow in FakeEngine.prefix_calls] == [
        (101, 12.5),
        (101, 25.0),
        (202, 12.5),
        (202, 25.0),
    ]

    # Every branch for a condition receives only that condition's fresh prefix.
    assert len(FakeEngine.future_calls) == len(conditions) * len(small_spec.branches)
    for token, prefix_token, _branch, _twindow in FakeEngine.future_calls:
        assert token == prefix_token
