"""Engine-v1 branch compatibility mappings and RNG namespace handling."""

from __future__ import annotations

from typing import Any

from .spec import BranchSpec, ExperimentSpec
from .validation import SpecValidationError, UnsupportedPolicyError


FROZEN_ENGINE_V1_NAMESPACE = (
    "continue",
    "reset_ema",
    "reset_B",
    "reset_B_ema",
    "B_carrier_only",
    "full_reset",
    "future_shuffle",
)

SUPPORTED_EXECUTED_BRANCHES: dict[str, dict[str, Any]] = {
    "continue": {
        "role": "control",
        "intervention_ids": (),
        "forcing_policy_id": None,
        "requires_rng": False,
    },
    "reset_ema": {
        "role": "state_intervention",
        "intervention_ids": ("engine_v1.reset_ema",),
        "forcing_policy_id": None,
        "requires_rng": False,
    },
    "reset_B": {
        "role": "state_intervention",
        "intervention_ids": ("engine_v1.reset_B",),
        "forcing_policy_id": None,
        "requires_rng": False,
    },
    "future_shuffle": {
        "role": "dynamic_forcing",
        "intervention_ids": (),
        "forcing_policy_id": "engine_v1.future_shuffle",
        "requires_rng": True,
    },
}


def validate_branch_compatibility(spec: ExperimentSpec) -> None:
    if tuple(spec.branch_rng_namespace) != FROZEN_ENGINE_V1_NAMESPACE:
        raise UnsupportedPolicyError(
            "The v1 T_window implementation requires the complete frozen seven-branch RNG namespace"
        )
    for branch in spec.branches:
        expected = SUPPORTED_EXECUTED_BRANCHES.get(branch.engine_branch)
        if expected is None:
            raise UnsupportedPolicyError(
                f"Engine-v1 modular runner does not execute branch {branch.engine_branch!r}"
            )
        if branch.name != branch.engine_branch:
            raise UnsupportedPolicyError(
                "Aliased branch names are not supported by the legacy compatibility collector"
            )
        for field in ("role", "intervention_ids", "forcing_policy_id", "requires_rng"):
            if getattr(branch, field) != expected[field]:
                raise SpecValidationError(
                    f"Branch {branch.name!r} {field}={getattr(branch, field)!r}; "
                    f"expected {expected[field]!r}"
                )

    if spec.study_id == "AIEF_1_4_S01":
        expected_order = ("continue", "reset_ema", "reset_B", "future_shuffle")
        observed_order = tuple(branch.engine_branch for branch in spec.branches)
        if observed_order != expected_order:
            raise SpecValidationError(
                f"S01 executed branch order {observed_order!r} != {expected_order!r}"
            )


def make_branch_rngs(engine: Any, seed: int, namespace: tuple[str, ...]) -> dict[str, Any]:
    """Delegate RNG creation to the certified engine using the full namespace."""
    if tuple(namespace) != FROZEN_ENGINE_V1_NAMESPACE:
        raise UnsupportedPolicyError("Cannot shorten or reorder the engine-v1 RNG namespace")
    rngs = engine.make_branch_rngs(int(seed), tuple(namespace))
    if tuple(rngs) != tuple(namespace):
        raise RuntimeError(
            f"Engine returned RNG mapping order {tuple(rngs)!r}, expected {tuple(namespace)!r}"
        )
    return rngs


def branch_rng_child_index(spec: ExperimentSpec, engine_branch: str) -> int:
    try:
        return spec.branch_rng_namespace.index(engine_branch)
    except ValueError as exc:
        raise KeyError(engine_branch) from exc
