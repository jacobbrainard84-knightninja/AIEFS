"""Explicit validation gates and typed failure classes."""

from __future__ import annotations

import math
from typing import Any

import numpy as np


class AIEFModularError(Exception):
    """Base class for expected platform failures."""


class SpecValidationError(AIEFModularError):
    pass


class BaselineGateError(AIEFModularError):
    pass


class ConditionSchemaError(AIEFModularError):
    pass


class ArtifactIntegrityError(AIEFModularError):
    pass


class UnsupportedPolicyError(AIEFModularError):
    pass


class ExecutionLockError(AIEFModularError):
    pass


class CatalogError(AIEFModularError):
    pass


def require_exact_branch_set(observed: dict[str, Any], expected: tuple[str, ...]) -> None:
    if tuple(observed) != expected:
        raise ConditionSchemaError(
            f"Branch set/order mismatch: observed={tuple(observed)!r}, expected={expected!r}"
        )


def validate_prefix_outputs(prefix: dict[str, Any], model: Any) -> None:
    required = (
        "B_at_split",
        "R_physical_past",
        "theta_at_split",
        "coherence_acc_at_split",
        "history_at_split",
        "selected_at_split",
    )
    missing = set(required) - set(prefix)
    if missing:
        raise ConditionSchemaError(f"Prefix missing keys: {sorted(missing)}")

    n = int(model.N)
    delay_steps = int(model.delay_steps)
    expected = {
        "B_at_split": ((n, n), np.dtype("float64")),
        "R_physical_past": ((n, n), np.dtype("float64")),
        "theta_at_split": ((n,), np.dtype("float64")),
        "coherence_acc_at_split": ((n, n), np.dtype("complex128")),
        "history_at_split": ((delay_steps + 1, n), np.dtype("float64")),
        "selected_at_split": ((n, n), np.dtype("uint8")),
    }
    for key, (shape, dtype) in expected.items():
        value = np.asarray(prefix[key])
        if value.shape != shape:
            raise ConditionSchemaError(f"Prefix {key} shape {value.shape} != {shape}")
        if value.dtype != dtype:
            raise ConditionSchemaError(f"Prefix {key} dtype {value.dtype} != {dtype}")
        if not np.all(np.isfinite(value)):
            raise ConditionSchemaError(f"Prefix {key} contains non-finite values")

    selected = np.asarray(prefix["selected_at_split"])
    if not np.all((selected == 0) | (selected == 1)):
        raise ConditionSchemaError("selected_at_split is not binary")


def _matrix_keys(engine: Any) -> tuple[str, ...]:
    try:
        keys = tuple(engine.REQUIRED_BRANCH_MATRIX_KEYS)
    except Exception as exc:
        raise ConditionSchemaError("Engine does not expose REQUIRED_BRANCH_MATRIX_KEYS") from exc
    return tuple(
        key
        for key in keys
        if key not in {"sample_times", "density_trajectory", "similarity_trajectory"}
    )


def validate_twindow_branch_output(
    *,
    engine: Any,
    branch: str,
    result: dict[str, Any],
    model: Any,
    protocol: Any,
    rho: float,
    required_scalar_keys: tuple[str, ...],
    primary_outcomes: tuple[str, ...],
    secondary_outcomes: tuple[str, ...],
) -> None:
    """Validate the complete legacy T_window condition branch contract."""
    required_matrices = tuple(engine.REQUIRED_BRANCH_MATRIX_KEYS)
    missing_scalar = set(required_scalar_keys) - set(result)
    missing_matrix = set(required_matrices) - set(result)
    if missing_scalar or missing_matrix:
        raise ConditionSchemaError(
            f"Branch {branch!r} missing scalars={sorted(missing_scalar)}, "
            f"matrices={sorted(missing_matrix)}"
        )

    n = int(model.N)
    for key in _matrix_keys(engine):
        array = np.asarray(result[key])
        if array.shape != (n, n):
            raise ConditionSchemaError(f"{branch}.{key} shape {array.shape} != {(n, n)}")
        if array.dtype != np.dtype("float64"):
            raise ConditionSchemaError(f"{branch}.{key} dtype {array.dtype} != float64")
        if not np.all(np.isfinite(array)):
            raise ConditionSchemaError(f"{branch}.{key} contains non-finite values")

    future_steps = int(protocol.future_steps(model))
    stride = int(protocol.diagnostic_stride)
    expected_times = (
        np.arange(0, future_steps, stride, dtype=float) + 1.0
    ) * float(model.dt)
    expected_length = len(expected_times)

    times = np.asarray(result["sample_times"])
    density = np.asarray(result["density_trajectory"])
    similarity = np.asarray(result["similarity_trajectory"])
    for key, array in (
        ("sample_times", times),
        ("density_trajectory", density),
        ("similarity_trajectory", similarity),
    ):
        if array.ndim != 1 or len(array) != expected_length:
            raise ConditionSchemaError(
                f"{branch}.{key} shape {array.shape} incompatible with {expected_length} samples"
            )
        if array.dtype != np.dtype("float64"):
            raise ConditionSchemaError(f"{branch}.{key} dtype {array.dtype} != float64")

    if not np.array_equal(times, expected_times):
        raise ConditionSchemaError(f"{branch}.sample_times has an unexpected schedule")
    if not np.all(np.isfinite(density)) or np.any((density < 0.0) | (density > 1.0)):
        raise ConditionSchemaError(f"{branch}.density_trajectory is outside [0,1] or non-finite")
    if np.any(np.isinf(similarity)):
        raise ConditionSchemaError(f"{branch}.similarity_trajectory contains Infinity")
    finite_similarity = similarity[np.isfinite(similarity)]
    if np.any((finite_similarity < -1.0 - 1e-12) | (finite_similarity > 1.0 + 1e-12)):
        raise ConditionSchemaError(f"{branch}.similarity_trajectory is outside [-1,1]")

    expected_twindow = float(model.T_window)
    if "rho" not in result or float(result["rho"]) != float(rho):
        raise ConditionSchemaError(f"{branch}.rho does not exactly match {rho!r}")
    if "T_window" not in result or float(result["T_window"]) != expected_twindow:
        raise ConditionSchemaError(
            f"{branch}.T_window does not exactly match {expected_twindow!r}"
        )

    window_steps = int(round(expected_twindow / float(model.dt)))
    recovery_end = min(5 * window_steps, future_steps)
    fixed_immediate = min(int(round(17.5 / float(model.dt))), future_steps)
    fixed_recovery = min(int(round(87.5 / float(model.dt))), future_steps)
    metadata = {
        "window_steps": window_steps,
        "recovery_end_ema": recovery_end,
        "fixed_immediate_end": fixed_immediate,
        "fixed_recovery_end": fixed_recovery,
    }
    for key, expected in metadata.items():
        observed = result.get(key)
        if isinstance(observed, bool) or not isinstance(observed, (int, np.integer)):
            raise ConditionSchemaError(f"{branch}.{key} is not an integer: {observed!r}")
        if int(observed) != expected:
            raise ConditionSchemaError(f"{branch}.{key}={observed} != {expected}")

    for key in primary_outcomes + secondary_outcomes:
        value = result.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)):
            raise ConditionSchemaError(f"{branch}.{key} is not numeric: {value!r}")
        if not np.isfinite(value):
            raise ConditionSchemaError(f"{branch}.{key} is non-finite: {value!r}")


def validate_s01_protocol_horizons(spec: Any) -> None:
    """Reject S01 configurations for which legacy horizon semantics are unavailable."""
    if getattr(spec, "study_id", None) != "AIEF_1_4_S01":
        return
    protocol = spec.protocol
    if (
        protocol.T_sim != 800.0
        or protocol.burn_end_time != 160.0
        or protocol.split_time != 480.0
        or protocol.future_duration != 320.0
        or protocol.diagnostic_stride != 50
    ):
        raise SpecValidationError(
            "S01 protocol must exactly match the certified 800/160/480/320/50 design"
        )
    if spec.seed_design.master_seed != 20260714 or spec.seed_design.count != 40:
        raise SpecValidationError("S01 requires master seed 20260714 and exactly 40 paired seeds")
    expected_seeds = tuple(
        int(child.generate_state(1, dtype=np.uint64)[0])
        for child in np.random.SeedSequence(20260714).spawn(40)
    )
    if tuple(spec.seed_design.paired_seeds) != expected_seeds:
        raise SpecValidationError("S01 paired seed cohort/order differs from the frozen design")
    expected_levels = (
        ("rho_0p50", 0.5),
        ("rho_0p75", 0.75),
        ("rho_1p00", 1.0),
        ("rho_1p50", 1.5),
        ("rho_2p00", 2.0),
    )
    if len(spec.model_axes) != 1:
        raise SpecValidationError("S01 requires exactly one rho axis")
    rho_axis = spec.model_axes[0]
    observed_levels = tuple((level.level_id, float(level.value)) for level in rho_axis.levels)
    if rho_axis.name != "rho" or observed_levels != expected_levels:
        raise SpecValidationError(
            f"S01 rho levels/order {observed_levels!r} != {expected_levels!r}"
        )
    if rho_axis.reference_level_id != "rho_1p00":
        raise SpecValidationError("S01 reference level must be rho_1p00")

    model = spec.base_model
    dt = float(model.dt)
    future_steps = int(round(protocol.future_duration / dt))
    fixed_immediate = int(round(17.5 / dt))
    fixed_recovery = int(round(87.5 / dt))
    if fixed_immediate <= 0 or fixed_recovery >= future_steps:
        raise SpecValidationError(
            "S01 fixed-physical immediate/recovery/late horizons must all be nonempty"
        )
    for axis in spec.model_axes:
        if axis.name != "rho":
            continue
        for level in axis.levels:
            t_window = float(level.value) * float(model.T_star)
            window_steps = int(round(t_window / dt))
            recovery_end = 5 * window_steps
            if window_steps <= 0:
                raise SpecValidationError(
                    f"S01 level {level.level_id} has an empty normalized immediate horizon"
                )
            if recovery_end >= future_steps:
                raise SpecValidationError(
                    f"S01 level {level.level_id} has an empty normalized late horizon"
                )


def exact_equal_with_nan(left: Any, right: Any) -> bool:
    """Exact scalar/array equality with matching NaN positions and dtypes."""
    a = np.asarray(left)
    b = np.asarray(right)
    if a.shape != b.shape or a.dtype != b.dtype:
        return False
    if np.issubdtype(a.dtype, np.complexfloating):
        # Compare real and imaginary components independently so a NaN in one
        # component does not hide a mismatch in the other.
        return exact_equal_with_nan(a.real, b.real) and exact_equal_with_nan(a.imag, b.imag)
    if np.issubdtype(a.dtype, np.floating):
        nan_a = np.isnan(a)
        nan_b = np.isnan(b)
        if not np.array_equal(nan_a, nan_b):
            return False
        return np.array_equal(a[~nan_a], b[~nan_b])
    return np.array_equal(a, b)


def exact_scalar_equal_with_nan(left: Any, right: Any) -> bool:
    try:
        a = float(left)
        b = float(right)
    except (TypeError, ValueError):
        return False
    if math.isnan(a) and math.isnan(b):
        return True
    return a == b
