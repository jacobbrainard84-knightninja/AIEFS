"""CLI invocation of AIEF_modular_driver_v1.py from its documented folder (R026-S7).

README_modular.md documents ``python AIEF_modular_driver_v1.py describe AIEF_1_4_S01`` run from this
platform folder. The driver and README are hash-pinned (registry/artifacts.csv ART-0064, ART-0068), so
neither is edited; ERRATA_2026-10-28.md gives the working invocation: put the repository root on
PYTHONPATH (from this folder ``PYTHONPATH=../.. python AIEF_modular_driver_v1.py ...``).

The first two tests are controls for that documented workaround. The third pins the known defect:
without the repository root on PYTHONPATH the certified engine module is not importable. It is a
strict xfail, so a future driver fix makes it XPASS and fails the run until the marker is removed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PLATFORM = Path(__file__).resolve().parents[1]
REPO_ROOT = PLATFORM.parents[1]
DRIVER = "AIEF_modular_driver_v1.py"


def _run(command: str, *, repo_root_on_path: bool) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if repo_root_on_path:
        env["PYTHONPATH"] = os.path.join("..", "..")  # relative to the platform folder, as documented
    return subprocess.run(
        [sys.executable, DRIVER, command, "AIEF_1_4_S01"],
        cwd=PLATFORM, env=env, capture_output=True, text=True, timeout=300,
    )


def test_layout_is_the_documented_one():
    assert (PLATFORM / DRIVER).is_file()
    assert (REPO_ROOT / "aief_experiment_engine_v1.py").is_file()


def test_describe_with_repo_root_on_pythonpath():
    proc = _run("describe", repo_root_on_path=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "SPECIFICATION ERROR" not in proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert len(payload["spec_sha256"]) == 64


def test_dry_run_with_repo_root_on_pythonpath():
    proc = _run("dry-run", repo_root_on_path=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "SPECIFICATION ERROR" not in proc.stdout + proc.stderr


@pytest.mark.xfail(strict=True, reason="R026-S7: driver (ART-0064, pinned) does not put the repo root "
                   "on sys.path; documented command fails without PYTHONPATH (see ERRATA)")
@pytest.mark.parametrize("command", ["describe", "dry-run"])
def test_documented_command_without_pythonpath(command):
    proc = _run(command, repo_root_on_path=False)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "SPECIFICATION ERROR" not in proc.stdout + proc.stderr
