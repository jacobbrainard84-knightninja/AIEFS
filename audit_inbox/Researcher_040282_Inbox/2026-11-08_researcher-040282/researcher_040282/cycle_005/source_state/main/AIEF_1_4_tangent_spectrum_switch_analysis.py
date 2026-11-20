#!/usr/bin/env python3
"""Tangent-rate, fixed-stratum Jacobian, and exceptional-switch analysis.

This script follows the corrected AIEF-1.4 tangent experiment. It:

* aggregates each fixed seed/direction across perturbation amplitudes;
* identifies unreliable/amplitude-clipped and genuinely slow tangent modes;
* compares frozen-fast and observed coupled contraction rates per direction;
* reconstructs fixed-active-stratum tangent Jacobians at selected mature states;
* analyzes eigenvalues, symmetric parts, non-normality, and transient growth;
* replays the exceptional seed and records node slack, row forcing, and alpha
  around its saturated-set transition.

No new broad simulation is run. The exceptional replay and short frozen-fast
finite differences use the already frozen split states.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import AIEF_1_4_stationarity_perturbation_analysis_updated as base
import AIEF_1_4_exceptional_tangent_analysis as tangent_source


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_SCALAR = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_scalar_summary.csv"
)
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_TANGENT_RESULTS = (
    "aief_1_4_exceptional_tangent/corrected_tangent_by_seed.csv"
)
DEFAULT_OUTPUT_DIR = "aief_1_4_tangent_spectrum_switch"
DEFAULT_EXCEPTIONAL_SEED = "4619122171158768524"
DEFAULT_MAX_JACOBIAN_SEEDS = 5
DEFAULT_JACOBIAN_STEP = 1e-5
DEFAULT_SWITCH_WINDOW = 25
DEFAULT_MIN_AMPLITUDE_FRACTION = 0.9
DEFAULT_MIN_RELATIVE_AMPLITUDE = 1e-6
DEFAULT_BOUNDARY_TOL = 1e-9
DEFAULT_TYPICAL_RATE = 0.315789
DEFAULT_SLOW_RATE_CUTOFF = 0.25
ZERO_TOL = 1e-14


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_inputs(
    scalar_path: str,
    tangent_path: str,
    manifest_path: str,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    for path in (scalar_path, tangent_path, manifest_path):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    scalar = pd.read_csv(scalar_path, dtype={"seed": str})
    tangent = pd.read_csv(tangent_path, dtype={"seed": str})
    scalar["seed"] = scalar["seed"].astype(str)
    tangent["seed"] = tangent["seed"].astype(str)
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    required = {
        "seed",
        "direction_id",
        "delta",
        "status",
        "amplitude_fraction_of_requested",
        "relative_actual_amplitude",
        "frozen_restoring_coefficient",
        "frozen_restoring_cosine",
        "observed_exponential_rate",
        "observed_exponential_r_squared",
    }
    missing = required - set(tangent.columns)
    if missing:
        raise ValueError(f"tangent result missing {sorted(missing)}")
    return scalar, tangent, manifest


def tangent_direction_summary(
    tangent: pd.DataFrame,
    min_amplitude_fraction: float,
    min_relative_amplitude: float,
    typical_rate: float,
    slow_rate_cutoff: float,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    valid_rows = tangent.loc[tangent["status"] == "ok"].copy()

    for (seed, direction_id), group in valid_rows.groupby(
        ["seed", "direction_id"]
    ):
        group = group.sort_values("delta")
        smallest = group.iloc[0]
        amplitude_fraction = float(smallest["amplitude_fraction_of_requested"])
        relative_amplitude = float(smallest["relative_actual_amplitude"])
        amplitude_reliable = bool(
            amplitude_fraction >= min_amplitude_fraction
            and relative_amplitude >= min_relative_amplitude
        )

        frozen = pd.to_numeric(
            group["frozen_restoring_coefficient"], errors="coerce"
        ).to_numpy(float)
        observed = pd.to_numeric(
            group["observed_exponential_rate"], errors="coerce"
        ).to_numpy(float)
        r_squared = pd.to_numeric(
            group["observed_exponential_r_squared"], errors="coerce"
        ).to_numpy(float)
        cosine = pd.to_numeric(
            group["frozen_restoring_cosine"], errors="coerce"
        ).to_numpy(float)

        frozen_finite = frozen[np.isfinite(frozen)]
        observed_finite = observed[np.isfinite(observed)]
        frozen_median = (
            float(np.median(frozen_finite)) if len(frozen_finite) else np.nan
        )
        observed_median = (
            float(np.median(observed_finite)) if len(observed_finite) else np.nan
        )
        absolute_error = (
            abs(frozen_median - observed_median)
            if np.isfinite(frozen_median) and np.isfinite(observed_median)
            else np.nan
        )
        relative_error = (
            absolute_error / abs(observed_median)
            if np.isfinite(absolute_error) and abs(observed_median) > ZERO_TOL
            else np.nan
        )
        typical_relative_error = (
            abs(observed_median - typical_rate) / typical_rate
            if np.isfinite(observed_median)
            else np.nan
        )

        rows.append(
            {
                "seed": seed,
                "direction_id": int(direction_id),
                "n_amplitudes": int(len(group)),
                "basis_dimension": int(smallest.get("basis_dimension", -1)),
                "support_size": int(smallest.get("support_size", -1)),
                "smallest_delta": float(smallest["delta"]),
                "smallest_requested_amplitude": float(
                    smallest.get("requested_amplitude", np.nan)
                ),
                "smallest_actual_amplitude": float(
                    smallest.get("actual_amplitude", np.nan)
                ),
                "amplitude_fraction_at_smallest_delta": amplitude_fraction,
                "relative_amplitude_at_smallest_delta": relative_amplitude,
                "amplitude_reliable": amplitude_reliable,
                "frozen_rate_median": frozen_median,
                "frozen_rate_min": float(np.nanmin(frozen)),
                "frozen_rate_max": float(np.nanmax(frozen)),
                "observed_rate_median": observed_median,
                "observed_rate_min": float(np.nanmin(observed)),
                "observed_rate_max": float(np.nanmax(observed)),
                "rate_absolute_error": absolute_error,
                "rate_relative_error": relative_error,
                "median_frozen_cosine": float(np.nanmedian(cosine)),
                "median_observed_R2": float(np.nanmedian(r_squared)),
                "typical_rate_relative_error": typical_relative_error,
                "within_1pct_typical_rate": bool(
                    np.isfinite(typical_relative_error)
                    and typical_relative_error <= 0.01
                ),
                "within_5pct_typical_rate": bool(
                    np.isfinite(typical_relative_error)
                    and typical_relative_error <= 0.05
                ),
                "within_10pct_typical_rate": bool(
                    np.isfinite(typical_relative_error)
                    and typical_relative_error <= 0.10
                ),
                "slow_observed_mode": bool(
                    np.isfinite(observed_median)
                    and observed_median < slow_rate_cutoff
                ),
                "negative_frozen_rate": bool(
                    np.isfinite(frozen_median) and frozen_median <= 0.0
                ),
            }
        )

    summary = pd.DataFrame(rows)
    anomalous = summary.loc[
        (~summary["amplitude_reliable"])
        | summary["slow_observed_mode"]
        | summary["negative_frozen_rate"]
        | (summary["rate_relative_error"] > 0.10)
    ].copy()

    reliable = summary.loc[summary["amplitude_reliable"]].copy()
    agreement = {
        "direction_count": int(len(summary)),
        "reliable_direction_count": int(len(reliable)),
        "amplitude_unreliable_count": int(
            np.sum(~summary["amplitude_reliable"])
        ),
        "slow_mode_count": int(np.sum(summary["slow_observed_mode"])),
        "negative_frozen_rate_count": int(
            np.sum(summary["negative_frozen_rate"])
        ),
        "within_1pct_typical_fraction": float(
            np.mean(reliable["within_1pct_typical_rate"])
        )
        if len(reliable)
        else np.nan,
        "within_5pct_typical_fraction": float(
            np.mean(reliable["within_5pct_typical_rate"])
        )
        if len(reliable)
        else np.nan,
        "within_10pct_typical_fraction": float(
            np.mean(reliable["within_10pct_typical_rate"])
        )
        if len(reliable)
        else np.nan,
        "median_frozen_rate": float(reliable["frozen_rate_median"].median())
        if len(reliable)
        else np.nan,
        "median_observed_rate": float(reliable["observed_rate_median"].median())
        if len(reliable)
        else np.nan,
        "median_rate_relative_error": float(
            reliable["rate_relative_error"].median()
        )
        if len(reliable)
        else np.nan,
        "pearson_frozen_observed": float(
            reliable[["frozen_rate_median", "observed_rate_median"]]
            .corr(method="pearson")
            .iloc[0, 1]
        )
        if len(reliable) >= 3
        else np.nan,
        "spearman_frozen_observed": float(
            reliable[["frozen_rate_median", "observed_rate_median"]]
            .corr(method="spearman")
            .iloc[0, 1]
        )
        if len(reliable) >= 3
        else np.nan,
    }
    return summary, anomalous, agreement


def state_field_components(
    state: base.DynamicState,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
) -> dict[str, Any]:
    _, F_matrix, _ = base.compute_field_and_updated_coherence(state, model)
    w = state.B[edges].copy()
    F = F_matrix[edges].copy()
    modified = base.positivity_direction(w, F)
    row_sum = A @ w
    slack = capacities - row_sum
    saturated = slack <= boundary_tolerance
    effective_capacity = capacities.copy()
    effective_capacity[saturated] = row_sum[saturated]
    d = A @ modified
    alpha = np.zeros(len(capacities), dtype=float)
    outward = saturated & (d > 0.0)
    alpha[outward] = d[outward] / effective_capacity[outward]
    field, info, _, _ = base.ideal_directional_field(
        w, F, A, capacities, boundary_tolerance
    )
    return {
        "w": w,
        "F": F,
        "modified_F": modified,
        "row_sum": row_sum,
        "slack": slack,
        "saturated": saturated,
        "d": d,
        "alpha": alpha,
        "field": field,
        "info": info,
    }


def exceptional_switch_diagnostics(
    data: Any,
    seed: str,
    manifest: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    switch_window: int,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    model = manifest["model"]
    future_steps = int(manifest["protocol"]["future_steps"])
    state = base.load_split_state(data, seed)
    previous_saturated: np.ndarray | None = None
    previous_outward: np.ndarray | None = None
    previous_components: dict[str, Any] | None = None
    all_rows: list[dict[str, Any]] = []
    switch_records: list[dict[str, Any]] = []
    switch_step: int | None = None

    for step in range(future_steps):
        components = state_field_components(
            state, model, capacities, A, edges, boundary_tolerance
        )
        saturated = components["saturated"]
        outward = components["d"] > 0.0
        saturated_changed = (
            previous_saturated is not None
            and not np.array_equal(saturated, previous_saturated)
        )
        outward_changed = (
            previous_outward is not None
            and not np.array_equal(outward, previous_outward)
        )
        if saturated_changed and switch_step is None:
            switch_step = step

        for node in range(len(capacities)):
            all_rows.append(
                {
                    "seed": seed,
                    "step": step,
                    "time_since_split": (step + 1) * float(model["dt"]),
                    "node": node,
                    "row_sum": float(components["row_sum"][node]),
                    "slack": float(components["slack"][node]),
                    "row_direction_d": float(components["d"][node]),
                    "alpha": float(components["alpha"][node]),
                    "saturated": bool(saturated[node]),
                    "outward": bool(outward[node]),
                    "saturated_changed": saturated_changed,
                    "outward_changed": outward_changed,
                    "P_F_norm": float(np.linalg.norm(components["field"])),
                    "P_F_over_F": float(
                        np.linalg.norm(components["field"])
                        / max(np.linalg.norm(components["F"]), ZERO_TOL)
                    ),
                }
            )

        if saturated_changed or outward_changed:
            changed_saturated = (
                np.flatnonzero(saturated != previous_saturated).tolist()
                if previous_saturated is not None
                else []
            )
            changed_outward = (
                np.flatnonzero(outward != previous_outward).tolist()
                if previous_outward is not None
                else []
            )
            switch_records.append(
                {
                    "seed": seed,
                    "step": step,
                    "time_since_split": (step + 1) * float(model["dt"]),
                    "saturated_changed": saturated_changed,
                    "outward_changed": outward_changed,
                    "changed_saturated_nodes": ";".join(
                        map(str, changed_saturated)
                    ),
                    "changed_outward_nodes": ";".join(map(str, changed_outward)),
                    "P_F_over_F": float(
                        np.linalg.norm(components["field"])
                        / max(np.linalg.norm(components["F"]), ZERO_TOL)
                    ),
                }
            )

        previous_saturated = saturated.copy()
        previous_outward = outward.copy()
        previous_components = components
        base.actual_step(
            state,
            model,
            capacities,
            A,
            edges,
            boundary_tolerance,
            audit_operator=False,
        )

    node_frame = pd.DataFrame(all_rows)
    if switch_step is not None:
        node_window = node_frame.loc[
            (node_frame["step"] >= max(0, switch_step - switch_window))
            & (node_frame["step"] <= switch_step + switch_window)
        ].copy()
    else:
        node_window = node_frame.iloc[0:0].copy()

    summary = {
        "seed": seed,
        "first_saturated_switch_step": switch_step,
        "first_saturated_switch_time": (
            (switch_step + 1) * float(model["dt"])
            if switch_step is not None
            else np.nan
        ),
        "switch_record_count": len(switch_records),
    }
    return node_window, pd.DataFrame(switch_records), summary


def tangent_basis_and_field(
    state: base.DynamicState,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    w = state.B[edges].copy()
    basis, _ = tangent_source.tangent_basis(
        w, A, capacities, boundary_tolerance
    )
    components = state_field_components(
        state, model, capacities, A, edges, boundary_tolerance
    )
    return w, basis, components["field"], components["F"]


def fixed_stratum_tangent_jacobian(
    state: base.DynamicState,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    relative_step: float,
) -> tuple[np.ndarray | None, dict[str, Any], list[dict[str, Any]]]:
    w, basis, base_field, _ = tangent_basis_and_field(
        state, model, capacities, A, edges, boundary_tolerance
    )
    dimension = basis.shape[1]
    if dimension == 0:
        return None, {"status": "empty_tangent_space"}, []

    norm_w = max(float(np.linalg.norm(w)), ZERO_TOL)
    columns: list[np.ndarray] = []
    direction_rows: list[dict[str, Any]] = []

    base_slack = capacities - A @ w
    base_saturated = base_slack <= boundary_tolerance
    base_zero = w <= ZERO_TOL

    for direction_id in range(dimension):
        direction = basis[:, direction_id]
        plus_limit = base.maximum_feasible_amplitude(w, direction, A, capacities)
        minus_limit = base.maximum_feasible_amplitude(w, -direction, A, capacities)
        requested = relative_step * norm_w
        step_size = min(requested, 0.25 * plus_limit, 0.25 * minus_limit)
        if not np.isfinite(step_size) or step_size <= 1e-12 * norm_w:
            return None, {
                "status": "jacobian_step_too_small",
                "failed_direction": direction_id,
                "requested_step": requested,
                "actual_step": step_size,
            }, direction_rows

        fields = []
        stratum_match = True
        for sign in (1.0, -1.0):
            perturbed_w = w + sign * step_size * direction
            perturbed_state = state.clone()
            perturbed_state.B = base.vector_to_matrix(
                perturbed_w, state.B.shape[0], edges
            )
            components = state_field_components(
                perturbed_state,
                model,
                capacities,
                A,
                edges,
                boundary_tolerance,
            )
            fields.append(components["field"])
            stratum_match &= bool(
                np.array_equal(components["saturated"], base_saturated)
                and np.array_equal(perturbed_w <= ZERO_TOL, base_zero)
            )

        derivative = (fields[0] - fields[1]) / (2.0 * step_size)
        tangent_column = basis.T @ derivative
        columns.append(tangent_column)
        direction_rows.append(
            {
                "record_type": "direction_finite_difference",
                "direction_id": direction_id,
                "requested_step": requested,
                "actual_step": step_size,
                "step_fraction_of_requested": step_size / requested,
                "stratum_preserved": stratum_match,
                "derivative_norm": float(np.linalg.norm(derivative)),
                "tangent_derivative_norm": float(np.linalg.norm(tangent_column)),
                "normal_leakage_norm": float(
                    np.linalg.norm(derivative - basis @ tangent_column)
                ),
            }
        )

    J = np.column_stack(columns)
    eigenvalues, eigenvectors = np.linalg.eig(J)
    symmetric_part = 0.5 * (J + J.T)
    symmetric_eigenvalues = np.linalg.eigvalsh(symmetric_part)
    singular_values = np.linalg.svd(J, compute_uv=False)
    commutator = J.T @ J - J @ J.T
    normality = float(
        np.linalg.norm(commutator)
        / max(np.linalg.norm(J) ** 2, ZERO_TOL)
    )
    eigenvector_condition = float(np.linalg.cond(eigenvectors))

    summary = {
        "status": "ok",
        "tangent_dimension": dimension,
        "spectral_abscissa": float(np.max(np.real(eigenvalues))),
        "slowest_decay_rate": float(-np.max(np.real(eigenvalues))),
        "median_real_eigenvalue": float(np.median(np.real(eigenvalues))),
        "symmetric_part_lambda_max": float(symmetric_eigenvalues[-1]),
        "symmetric_part_lambda_min": float(symmetric_eigenvalues[0]),
        "largest_singular_value": float(singular_values[0]),
        "smallest_singular_value": float(singular_values[-1]),
        "eigenvector_condition_number": eigenvector_condition,
        "normality_commutator_ratio": normality,
        "base_field_norm": float(np.linalg.norm(base_field)),
        "all_directions_preserved_stratum": bool(
            all(row["stratum_preserved"] for row in direction_rows)
        ),
    }

    eigen_rows = [
        {
            "record_type": "eigenvalue",
            "mode": index,
            "eigenvalue_real": float(np.real(value)),
            "eigenvalue_imag": float(np.imag(value)),
        }
        for index, value in enumerate(eigenvalues)
    ]
    return J, summary, direction_rows + eigen_rows


def transient_growth_curve(
    J: np.ndarray,
    max_time: float,
    samples: int,
) -> pd.DataFrame:
    eigenvalues, eigenvectors = np.linalg.eig(J)
    inverse = np.linalg.inv(eigenvectors)
    rows: list[dict[str, Any]] = []
    for time_value in np.linspace(0.0, max_time, samples):
        exponential = (
            eigenvectors
            @ np.diag(np.exp(eigenvalues * time_value))
            @ inverse
        )
        norm = float(np.linalg.norm(exponential, ord=2))
        rows.append(
            {
                "time": float(time_value),
                "propagator_norm_2": norm,
            }
        )
    return pd.DataFrame(rows)


def make_report(
    direction_agreement: dict[str, Any],
    exceptional_summary: dict[str, Any],
    jacobian_summary: pd.DataFrame,
) -> str:
    lines = [
        "AIEF tangent-spectrum and exceptional-switch analysis",
        "======================================================",
        "",
        "Tangent direction agreement",
        "---------------------------",
    ]
    for key, value in direction_agreement.items():
        lines.append(f"  {key}: {value}")

    lines.extend(["", "Exceptional switch", "------------------"])
    for key, value in exceptional_summary.items():
        lines.append(f"  {key}: {value}")

    lines.extend(["", "Fixed-stratum tangent Jacobians", "--------------------------------"])
    for _, row in jacobian_summary.iterrows():
        lines.append(
            f"  seed={row['seed']}: status={row['status']}, "
            f"dimension={row.get('tangent_dimension', np.nan)}, "
            f"spectral_abscissa={row.get('spectral_abscissa', np.nan)}, "
            f"slowest_rate={row.get('slowest_decay_rate', np.nan)}, "
            f"sym_part_max={row.get('symmetric_part_lambda_max', np.nan)}, "
            f"normality={row.get('normality_commutator_ratio', np.nan)}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* The tangent Jacobian is a frozen-fast, fixed-stratum finite-difference object.",
            "* Directions with inadequate two-sided feasible steps are rejected.",
            "* The r2 B_carrier_only/full_reset contrast remains unrelated to this analysis.",
            "* A negative spectral abscissa supports local tangent contraction but does not prove full coupled stability.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scalar", default=DEFAULT_SCALAR)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--tangent-results", default=DEFAULT_TANGENT_RESULTS)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--exceptional-seed", default=DEFAULT_EXCEPTIONAL_SEED)
    parser.add_argument(
        "--max-jacobian-seeds", type=int, default=DEFAULT_MAX_JACOBIAN_SEEDS
    )
    parser.add_argument(
        "--jacobian-step", type=float, default=DEFAULT_JACOBIAN_STEP
    )
    parser.add_argument(
        "--switch-window", type=int, default=DEFAULT_SWITCH_WINDOW
    )
    parser.add_argument(
        "--min-amplitude-fraction",
        type=float,
        default=DEFAULT_MIN_AMPLITUDE_FRACTION,
    )
    parser.add_argument(
        "--min-relative-amplitude",
        type=float,
        default=DEFAULT_MIN_RELATIVE_AMPLITUDE,
    )
    parser.add_argument(
        "--boundary-tol", type=float, default=DEFAULT_BOUNDARY_TOL
    )
    parser.add_argument("--typical-rate", type=float, default=DEFAULT_TYPICAL_RATE)
    parser.add_argument(
        "--slow-rate-cutoff", type=float, default=DEFAULT_SLOW_RATE_CUTOFF
    )
    parser.add_argument("--transient-time", type=float, default=15.0)
    parser.add_argument("--transient-samples", type=int, default=151)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.scalar, args.npz, args.manifest, args.tangent_results):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if (
        args.max_jacobian_seeds < 0
        or args.jacobian_step <= 0.0
        or args.switch_window < 0
        or args.boundary_tol < 0.0
        or args.transient_time <= 0.0
        or args.transient_samples < 2
    ):
        raise ValueError("invalid command-line settings")
    os.makedirs(args.output_dir, exist_ok=True)

    scalar, tangent, manifest = load_inputs(
        args.scalar, args.tangent_results, args.manifest
    )
    direction_summary, anomalous, agreement = tangent_direction_summary(
        tangent,
        args.min_amplitude_fraction,
        args.min_relative_amplitude,
        args.typical_rate,
        args.slow_rate_cutoff,
    )

    model = manifest["model"]
    node_count = int(model["N"])
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(node_count, capacity)
    A, edges = base.incidence_matrix(node_count)
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    jacobian_seeds = (
        seeds if args.max_jacobian_seeds == 0 else seeds[: args.max_jacobian_seeds]
    )

    jacobian_rows: list[dict[str, Any]] = []
    jacobian_direction_rows: list[dict[str, Any]] = []
    transient_rows: list[pd.DataFrame] = []
    jacobian_matrices: dict[str, np.ndarray] = {}

    with np.load(args.npz, allow_pickle=False) as data:
        exceptional_window, exceptional_switches, exceptional_summary = (
            exceptional_switch_diagnostics(
                data,
                args.exceptional_seed,
                manifest,
                capacities,
                A,
                edges,
                args.boundary_tol,
                args.switch_window,
            )
        )

        for seed in jacobian_seeds:
            state = base.load_split_state(data, seed)
            J, summary, direction_rows = fixed_stratum_tangent_jacobian(
                state,
                model,
                capacities,
                A,
                edges,
                args.boundary_tol,
                args.jacobian_step,
            )
            jacobian_rows.append({"seed": seed, **summary})
            for row in direction_rows:
                jacobian_direction_rows.append({"seed": seed, **row})
            if J is not None:
                jacobian_matrices[f"seed_{seed}_J_tangent"] = J
                curve = transient_growth_curve(
                    J, args.transient_time, args.transient_samples
                )
                curve.insert(0, "seed", seed)
                transient_rows.append(curve)

    jacobian_summary = pd.DataFrame(jacobian_rows)
    direction_details = pd.DataFrame(jacobian_direction_rows)
    transient = (
        pd.concat(transient_rows, ignore_index=True)
        if transient_rows
        else pd.DataFrame()
    )

    outputs = {
        "tangent_direction_summary.csv": direction_summary,
        "anomalous_tangent_directions.csv": anomalous,
        "exceptional_switch_node_window.csv": exceptional_window,
        "exceptional_switch_events.csv": exceptional_switches,
        "tangent_jacobian_summary.csv": jacobian_summary,
        "tangent_jacobian_direction_details.csv": direction_details,
        "tangent_transient_growth.csv": transient,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(args.output_dir, filename), index=False)
    np.savez_compressed(
        os.path.join(args.output_dir, "tangent_jacobian_matrices.npz"),
        **jacobian_matrices,
    )

    with open(
        os.path.join(args.output_dir, "direction_agreement_summary.json"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(agreement, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(
        os.path.join(args.output_dir, "exceptional_switch_summary.json"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(exceptional_summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    report = make_report(agreement, exceptional_summary, jacobian_summary)
    with open(
        os.path.join(args.output_dir, "tangent_spectrum_switch_report.txt"),
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(report)
    print(report)

    analysis_manifest = {
        "analysis": "AIEF tangent spectrum and exceptional switch",
        "scalar_path": str(Path(args.scalar).resolve()),
        "scalar_sha256": file_sha256(args.scalar),
        "npz_path": str(Path(args.npz).resolve()),
        "npz_sha256": file_sha256(args.npz),
        "source_manifest_path": str(Path(args.manifest).resolve()),
        "source_manifest_sha256": file_sha256(args.manifest),
        "tangent_results_path": str(Path(args.tangent_results).resolve()),
        "tangent_results_sha256": file_sha256(args.tangent_results),
        "exceptional_seed": args.exceptional_seed,
        "jacobian_seeds": jacobian_seeds,
        "jacobian_relative_step": args.jacobian_step,
        "minimum_amplitude_fraction": args.min_amplitude_fraction,
        "minimum_relative_amplitude": args.min_relative_amplitude,
        "boundary_tolerance": args.boundary_tol,
        "typical_rate": args.typical_rate,
        "slow_rate_cutoff": args.slow_rate_cutoff,
        "notes": [
            "B_carrier_only/full_reset phase matching is not part of this analysis.",
            "The Jacobian is frozen-fast and fixed-stratum.",
            "The exceptional switch is analyzed through node slack, row forcing, and alpha.",
        ],
    }
    with open(
        os.path.join(args.output_dir, "analysis_manifest.json"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(analysis_manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(f"Saved analysis to {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
