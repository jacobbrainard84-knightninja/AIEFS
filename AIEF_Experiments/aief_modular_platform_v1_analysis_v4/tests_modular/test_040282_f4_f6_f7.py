"""Independent synthetic regressions for ERRATA E19/E20/E21; no inbox code/data.

Pinned false results are deliberately asserted as historical defects, not endorsed.
Successors must reject the same negatives without weakening existing modular tests.
"""
from __future__ import annotations

import ast
from pathlib import Path
import types
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import AIEF_1_4_proposal_equalization_bridge_analysis as original_bridge
import AIEF_1_4_proposal_equalization_bridge_analysis_v1_1 as bridge
import aief_experiment_engine_v1 as engine
from aief_modular import oracle, oracle_v1_1
from aief_modular.validation import exact_equal_with_nan


BAD = (0.41, 0.31, 0.27)
GOOD = (0.41, 0.27, 0.31)
ROWS = "seed,rho,status\n101,0.5,passed\n202,1.0,passed\n"


def test_f4_pinned_false_pass_is_preserved(capsys):
    original_bridge.synthetic_self_test()
    assert "checks: PASS" in capsys.readouterr().out
    result = bridge.synthetic_projection_diagnostics(BAD)
    assert result["winners"] == {25: 2, 29: 2, 59: 7}
    assert result["left_residual"] == pytest.approx(-0.02121459694983044, abs=1e-15)
    with pytest.raises(ValueError, match="outside the expected winner branch"):
        bridge.check_synthetic_projection(BAD)
    assert "PASS" not in capsys.readouterr().out


def test_f4_real_operator_positive_control():
    result = bridge.check_synthetic_projection(GOOD)
    assert result["winners"] == {25: 7, 29: 2, 59: 7}
    assert abs(result["left_residual"]) < 1e-14
    assert abs(result["right_residual"]) < 1e-14


def _self_test_contract(monkeypatch, capsys):
    real_operator = bridge.admissibility.admissibility_from_nonnegative_proposal
    seen = []

    def spy(x, *args):
        seen.append(tuple(x[[25, 29, 59]]))
        return real_operator(x, *args)

    monkeypatch.setattr(bridge.admissibility, "admissibility_from_nonnegative_proposal", spy)
    bridge.synthetic_self_test()
    output = capsys.readouterr().out
    assert BAD in seen and GOOD in seen, "self-test bypassed the real operator fixtures"
    assert "checks: PASS" in output


def test_f4_successor_self_test_contract(monkeypatch, capsys):
    _self_test_contract(monkeypatch, capsys)


def test_f4_contract_kills_old_hardcoded_pass_mutant(monkeypatch, capsys):
    # Mutation back to the pinned old function must fail the same contract.
    mutant = types.FunctionType(original_bridge.synthetic_self_test.__code__, bridge.__dict__)
    monkeypatch.setattr(bridge, "synthetic_self_test", mutant)
    with pytest.raises(AssertionError, match="bypassed the real operator"):
        _self_test_contract(monkeypatch, capsys)


def test_f4_self_test_rejects_accept_all_mutant(monkeypatch, capsys):
    monkeypatch.setattr(bridge, "check_synthetic_projection", lambda values: {})
    with pytest.raises(ValueError, match="Known-false old fixture was accepted"):
        bridge.synthetic_self_test()
    assert "PASS" not in capsys.readouterr().out


def test_f4_bad_operator_output_cannot_print_pass(monkeypatch, capsys):
    real_operator = bridge.admissibility.admissibility_from_nonnegative_proposal

    def hardcoded_operator(x, *args):
        y, branch = real_operator(x, *args)
        # Reintroduce the original error: project each selected edge using the
        # assumed winner, rather than the winner returned by the real operator.
        for edge, winner in original_bridge.EXPECTED_WINNERS.items():
            y[edge] = branch["scales"][winner] * x[edge]
            branch["winner_code"][edge] = winner
        return y, branch

    monkeypatch.setattr(bridge.admissibility, "admissibility_from_nonnegative_proposal", hardcoded_operator)
    with pytest.raises(ValueError, match="Negative-control winner mismatch"):
        bridge.synthetic_self_test()
    assert "PASS" not in capsys.readouterr().out


@pytest.mark.parametrize("left,right", [
    (complex(float("nan"), 1), complex(float("nan"), 99)),
    (complex(1, float("nan")), complex(2, float("nan"))),
])
def test_f6_frozen_engine_known_defect_modular_required_reject(left, right):
    a, b = np.array([left]), np.array([right])
    assert engine.exact_array_equal_with_nan(a, b)  # known defect, E20
    assert not exact_equal_with_nan(a, b)  # required correct rejection
    assert not exact_equal_with_nan(b, a)


def test_f6_prefix_max_diff_expression_known_defect():
    # Execute the actual three pinned production statements in isolation, not a
    # hand-rewritten mask or a full expensive baseline run. This diagnostic is
    # normally reached only after an exact-comparison failure.
    tree = ast.parse(Path(engine.__file__).read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_baseline_equivalence")
    statements = {n.lineno: n for n in ast.walk(function) if isinstance(n, ast.Assign)}
    starts = [n for n in statements.values() if isinstance(n.targets[0], ast.Name) and n.targets[0].id == "e"
              and "engine_val" in ast.unparse(n.value)]
    first = min(starts, key=lambda n: n.lineno)
    block = ast.Module(body=[statements[first.lineno + i] for i in range(3)], type_ignores=[])
    scope = dict(np=np, engine_val=np.array([complex(float("nan"), 1)]),
                 frozen_val=np.array([complex(float("nan"), 99)]),
                 seed_results={"max_diffs": {}}, key="witness")
    exec(compile(block, engine.__file__, "exec"), scope)
    assert scope["seed_results"]["max_diffs"]["prefix_witness"] == 0.0


@pytest.fixture
def run_pair(tmp_path):
    dirs = [tmp_path / name for name in ("candidate", "oracle")]
    for directory in dirs:
        directory.mkdir()
        (directory / "AIEF_1_4_Twindow_sensitivity_fixture_scalar_summary.csv").write_text(
            "seed,branch,value\n101,continue,1.0\n")
        np.savez(directory / "AIEF_1_4_Twindow_sensitivity_fixture_branch_diagnostics.npz", value=np.array([1.0]))
        (directory / "twindow_condition_status.csv").write_text(ROWS)
    return dirs


def test_f7_pinned_accepts_successor_rejects_duplicate(run_pair):
    candidate, reference = run_pair
    (candidate / "twindow_condition_status.csv").write_text(ROWS + "101,0.5,passed\n")
    old = oracle.compare_twindow_run(candidate, reference)
    assert old.status == "passed" and old.condition_rows == 3 and not old.errors
    new = oracle_v1_1.compare_twindow_run(candidate, reference)
    assert new.status == "failed" and new.condition_rows == 3
    assert any("row count differs" in error for error in new.errors)
    assert any("duplicate" in error for error in new.errors)


def test_f7_successor_matching_pair_passes(run_pair):
    result = oracle_v1_1.compare_twindow_run(*run_pair)
    assert result.status == "passed" and result.condition_rows == 2 and not result.errors


@pytest.mark.parametrize("rows", [
    "seed,rho,status\n101,0.5,passed\n",  # missing row
    ROWS.replace("202,1.0,passed", "202,1.0,failed"),  # changed status
    "seed,rho,status\n101,0.5,passed\n101,0.5,passed\n",  # replacement duplicate
])
def test_f7_existing_negative_controls_still_fail(run_pair, rows):
    (run_pair[0] / "twindow_condition_status.csv").write_text(rows)
    assert oracle.compare_twindow_run(*run_pair).status == "failed"
    assert oracle_v1_1.compare_twindow_run(*run_pair).status == "failed"


@pytest.mark.parametrize("side", [0, 1, 2])
def test_f7_duplicate_on_either_or_both_sides_rejected(run_pair, side):
    for index, directory in enumerate(run_pair):
        if index == side or side == 2:
            (directory / "twindow_condition_status.csv").write_text(ROWS + "101,0.50,passed\n")
    result = oracle_v1_1.compare_twindow_run(*run_pair)
    assert result.status == "failed"
    assert any("duplicate" in error for error in result.errors)
