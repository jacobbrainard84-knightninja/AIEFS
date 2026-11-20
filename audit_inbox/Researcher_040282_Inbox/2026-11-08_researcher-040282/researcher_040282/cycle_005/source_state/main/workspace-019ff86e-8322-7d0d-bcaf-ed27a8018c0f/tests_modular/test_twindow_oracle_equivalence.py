from __future__ import annotations

import os
from pathlib import Path

import pytest

from aief_modular.oracle import compare_twindow_run


def _paths():
    candidate = os.environ.get("AIEF_MODULAR_RUN")
    oracle = os.environ.get("AIEF_TWINDOW_ORACLE", "runs/b57562a8ee77")
    return Path(candidate) if candidate else None, Path(oracle)


def test_full_logical_oracle_equivalence_when_runs_are_supplied():
    candidate, oracle = _paths()
    if candidate is None or not candidate.is_dir() or not oracle.is_dir():
        pytest.skip("set AIEF_MODULAR_RUN and provide runs/b57562a8ee77 for oracle equivalence")
    result = compare_twindow_run(candidate, oracle)
    assert result.status == "passed", "\n".join(result.errors[:20])
    assert result.scalar_rows == 800
    assert result.condition_rows == 200
