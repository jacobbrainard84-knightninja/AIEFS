from __future__ import annotations

import importlib.util
import os

import pytest


ENGINE_AVAILABLE = importlib.util.find_spec("aief_experiment_engine_v1") is not None
RUN_SLOW = os.environ.get("AIEF_RUN_SLOW_TESTS") == "1"


@pytest.mark.skipif(not ENGINE_AVAILABLE, reason="authoritative engine not present in scaffold workspace")
@pytest.mark.skipif(not RUN_SLOW, reason="set AIEF_RUN_SLOW_TESTS=1 for the 176k-step smoke")
def test_twindow_one_condition_round_trip(tmp_path):
    from aief_modular.artifacts import atomic_write_npz, load_npz
    from aief_modular.collectors import TWindowLegacyCollectorV1
    from aief_modular.factors import expand_conditions
    from aief_modular.registry import REGISTRY, load_builtin_studies
    from aief_modular.runner import _simulate_condition

    load_builtin_studies()
    spec = REGISTRY.get("AIEF_1_4_S01").build()
    engine = __import__(spec.engine_module)
    condition = expand_conditions(spec)[0]
    collector = TWindowLegacyCollectorV1()
    rows, payload = _simulate_condition(
        engine=engine,
        spec=spec,
        condition=condition,
        collector=collector,
    )
    assert condition.value("rho") == 0.5
    assert len(rows) == 4
    assert tuple(row["branch"] for row in rows) == (
        "continue", "reset_ema", "reset_B", "future_shuffle"
    )
    path = tmp_path / "condition.npz"
    atomic_write_npz(path, payload)
    observed = load_npz(path)
    assert set(observed) == set(payload)
