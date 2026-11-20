"""Raw-observable collectors for modular experiment execution.

Collectors deliberately perform no seed-level inference, bootstrap, or DID
analysis.  The T_window compatibility collector preserves the successful
production driver's flat CSV/NPZ contract.
"""

from __future__ import annotations

from typing import Any, Protocol

import numpy as np

from .factors import Condition
from .spec import CollectorSpec
from .validation import (
    ConditionSchemaError,
    SpecValidationError,
    UnsupportedPolicyError,
    validate_prefix_outputs,
    validate_twindow_branch_output,
)


class Collector(Protocol):
    collector_id: str
    schema_version: str
    core_schema_version: str
    study_schema_version: str

    def validate_engine_result(
        self,
        *,
        engine: Any,
        condition: Condition,
        model: Any,
        protocol: Any,
        prefix: dict[str, Any],
        branch_results: dict[str, dict[str, Any]],
    ) -> None: ...

    def scalar_rows(
        self,
        *,
        condition: Condition,
        branch_results: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]: ...

    def array_payload(
        self,
        *,
        condition: Condition,
        model: Any,
        prefix: dict[str, Any],
        branch_results: dict[str, dict[str, Any]],
    ) -> dict[str, Any]: ...


CONDITION_LOCAL_LEGACY_SCALAR_KEYS = (
    "D_B_final",
    "P_mean_full",
    "P_mean_immediate",
    "P_mean_recovery",
    "P_mean_late",
    "Weighted_similarity_final",
    "Weighted_similarity_late",
    "Jaccard_final",
    "Retention_selected_late",
    "Emergence_unselected_late",
    "Retention_contrast_late",
    "Corr_Rpast_Pfull",
    "Corr_Rpast_Plate",
    "Total_edge_weight",
    "Mean_row_sum",
    "Max_row_sum",
    "Nonzero_edge_fraction",
    "Effective_edges",
    "Weight_gini",
    "Weight_entropy",
    "r_mean_future",
    "r_mean_late",
    "Minimum_similarity",
    "G_min_future",
    "G_min_pre_future",
    "Pre_gap_violation_fraction",
    "Projection_active_fraction",
    "Projection_active_given_violation",
    "Projection_norm_mean_active",
    "Projection_norm_max",
    "Projection_relative_state_mean_active",
    "Projection_relative_state_max",
    "Projection_relative_update_mean_active",
    "Projection_relative_update_max",
)

EXTENDED_STUDY_SCALAR_KEYS = (
    "P_mean_late_fixed_physical",
    "Weighted_similarity_late_fixed_physical",
    "Retention_contrast_late_fixed_physical",
    "Corr_Rpast_Plate_fixed_physical",
    "r_mean_late_fixed_physical",
    "P_mean_late_normalized_EMA",
    "Weighted_similarity_late_normalized_EMA",
    "Retention_contrast_late_normalized_EMA",
    "Corr_Rpast_Plate_normalized_EMA",
    "r_mean_late_normalized_EMA",
)

EXPECTED_ENGINE_EXTENDED_SCALAR_KEYS = (
    "P_mean_late_fixed_physical",
    "Weighted_similarity_late_fixed_physical",
    "Retention_contrast_late_fixed_physical",
    "Corr_Rpast_Plate_fixed_physical",
    "r_mean_late_fixed_physical",
    "P_mean_late_normalized_EMA",
    "Weighted_similarity_late_normalized_EMA",
    "Retention_contrast_late_normalized_EMA",
    "Corr_Rpast_Plate_normalized_EMA",
    "r_mean_late_normalized_EMA",
    "P_mean_full_fixed_physical",
    "P_mean_immediate_fixed_physical",
    "P_mean_recovery_fixed_physical",
    "P_mean_full_normalized_EMA",
    "P_mean_immediate_normalized_EMA",
    "P_mean_recovery_normalized_EMA",
    "Retention_selected_late_fixed_physical",
    "Emergence_unselected_late_fixed_physical",
    "Retention_selected_late_normalized_EMA",
    "Emergence_unselected_late_normalized_EMA",
    "Corr_Rpast_Pfull_fixed_physical",
    "Corr_Rpast_Pfull_normalized_EMA",
    "Jaccard_final_fixed_physical",
)

REQUIRED_STUDY_SCALAR_KEYS = CONDITION_LOCAL_LEGACY_SCALAR_KEYS + EXTENDED_STUDY_SCALAR_KEYS
PRIMARY_OUTCOMES = (
    "Weighted_similarity_late_fixed_physical",
    "Retention_contrast_late_fixed_physical",
    "P_mean_late_fixed_physical",
)
SECONDARY_OUTCOMES = (
    "Weighted_similarity_late_normalized_EMA",
    "Retention_contrast_late_normalized_EMA",
    "P_mean_late_normalized_EMA",
)


class TWindowLegacyCollectorV1:
    collector_id = "aief.twindow.legacy-flat"
    schema_version = "v1"
    core_schema_version = "aief-engine-v1-raw-v1"
    study_schema_version = "aief-1.4-s01-twindow-v1"

    @staticmethod
    def _rho(condition: Condition) -> float:
        return float(condition.value("rho"))

    def validate_engine_result(
        self,
        *,
        engine: Any,
        condition: Condition,
        model: Any,
        protocol: Any,
        prefix: dict[str, Any],
        branch_results: dict[str, dict[str, Any]],
    ) -> None:
        validate_prefix_outputs(prefix, model)
        if tuple(branch_results) != condition.expected_branches:
            raise ConditionSchemaError(
                f"Condition {condition.condition_id} branch set/order {tuple(branch_results)!r} "
                f"!= {condition.expected_branches!r}"
            )
        rho = self._rho(condition)
        # Direct simulate_future() does not yet contain the eight historical
        # cross-branch fields added by finalize_historical_branch_metrics().
        # It must, however, contain every other frozen scalar and every extended
        # scalar exposed by engine v1, including fields not selected for the CSV.
        extended_engine_keys = tuple(getattr(engine, "EXTENDED_BRANCH_SCALAR_KEYS", ()))
        if extended_engine_keys != EXPECTED_ENGINE_EXTENDED_SCALAR_KEYS:
            raise SpecValidationError(
                "Engine extended scalar schema differs from the legacy collector contract: "
                f"observed={extended_engine_keys!r}, "
                f"expected={EXPECTED_ENGINE_EXTENDED_SCALAR_KEYS!r}"
            )
        direct_engine_scalar_keys = CONDITION_LOCAL_LEGACY_SCALAR_KEYS + extended_engine_keys
        required_engine_scalars = tuple(dict.fromkeys(direct_engine_scalar_keys + REQUIRED_STUDY_SCALAR_KEYS))
        for branch, result in branch_results.items():
            validate_twindow_branch_output(
                engine=engine,
                branch=branch,
                result=result,
                model=model,
                protocol=protocol,
                rho=rho,
                required_scalar_keys=required_engine_scalars,
                primary_outcomes=PRIMARY_OUTCOMES,
                secondary_outcomes=SECONDARY_OUTCOMES,
            )

    def scalar_rows(
        self,
        *,
        condition: Condition,
        branch_results: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        rho = self._rho(condition)
        rows: list[dict[str, Any]] = []
        for branch, result in branch_results.items():
            row: dict[str, Any] = {
                "seed_index": condition.seed_index,
                "seed": condition.seed,
                "rho": rho,
                "T_window": result["T_window"],
                "branch": branch,
            }
            for key in REQUIRED_STUDY_SCALAR_KEYS:
                if key not in result:
                    raise ConditionSchemaError(f"{branch} missing scalar {key}")
                value = result[key]
                scalar = np.asarray(value)
                if scalar.ndim != 0:
                    raise ConditionSchemaError(
                        f"{branch} scalar {key} has non-scalar shape {scalar.shape}"
                    )
                if np.issubdtype(scalar.dtype, np.complexfloating):
                    raise ConditionSchemaError(f"{branch} scalar {key} is complex")
                row[key] = value
            rows.append(row)
        return rows

    def array_payload(
        self,
        *,
        condition: Condition,
        model: Any,
        prefix: dict[str, Any],
        branch_results: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Preserve the successful driver's complete flat NPZ logical contract.

        Although this is called an array payload, the oracle driver also placed
        zero-dimensional scalar metadata in the NPZ.  Those entries are retained
        for strict workflow compatibility in v1.
        """
        seed = condition.seed
        rho = self._rho(condition)
        rho_text = str(rho)  # legacy key formatting used by analysis_v3
        payload: dict[str, Any] = {
            f"seed_{seed}_rho_{rho_text}_config_T_window": model.T_window,
            f"seed_{seed}_rho_{rho_text}_config_alpha": model.alpha,
        }
        for key, value in prefix.items():
            payload[f"prefix_seed_{seed}_rho_{rho_text}_{key}"] = value
        for branch, result in branch_results.items():
            for key, value in result.items():
                payload[f"{branch}_seed_{seed}_rho_{rho_text}_{key}"] = value
        return payload

    def scalar_fieldnames(self) -> tuple[str, ...]:
        return (
            "seed_index",
            "seed",
            "rho",
            "T_window",
            "branch",
            *REQUIRED_STUDY_SCALAR_KEYS,
        )

    def checkpoint_filename(self, condition: Condition) -> str:
        rho = self._rho(condition)
        return f"condition_seed_{condition.seed}_rho_{rho:.2f}.npz"


def build_collector(spec: CollectorSpec) -> Collector:
    if spec.collector_id != TWindowLegacyCollectorV1.collector_id:
        raise UnsupportedPolicyError(f"Unknown collector ID: {spec.collector_id}")
    expected_versions = (
        TWindowLegacyCollectorV1.schema_version,
        TWindowLegacyCollectorV1.core_schema_version,
        TWindowLegacyCollectorV1.study_schema_version,
    )
    observed_versions = (
        spec.schema_version,
        spec.core_schema_version,
        spec.study_schema_version,
    )
    if observed_versions != expected_versions:
        raise SpecValidationError(
            f"Collector schema mismatch: spec={observed_versions!r}, implementation={expected_versions!r}"
        )
    return TWindowLegacyCollectorV1()
