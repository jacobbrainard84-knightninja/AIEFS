#!/usr/bin/env python3
"""Active-face fingerprints and analytic/numerical tangent spectra for AIEF-1.4.

This script implements the immediate operator-theoretic work:

* build active-face fingerprints for all mature split states;
* derive the fixed-stratum analytic tangent Jacobian;
* recompute numerical tangent Jacobians over a finite-difference step grid;
* compare matrices and spectra;
* reconstruct exceptional-seed Jacobians before and after its face switch;
* cross-tab corrected tangent recovery rates against face classes;
* filter amplitude-clipped or stratum-changing tangent directions.

The analytic fixed-stratum formula assumes:
* positive-edge support is fixed;
* saturated/outward node sets are fixed;
* endpoint alpha ordering is fixed;
* perturbations are tangent to all saturated rows.

Under these assumptions, d(alpha)=0 along tangent directions and

    J_T = Q_T^T diag(-gamma - max(alpha_i,alpha_j)) Q_T.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

import AIEF_1_4_stationarity_perturbation_analysis_updated as base
import AIEF_1_4_exceptional_tangent_analysis as tangent_source
import AIEF_1_4_tangent_spectrum_switch_analysis as previous_analysis


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
DEFAULT_OUTPUT_DIR = "aief_1_4_face_spectrum"
DEFAULT_EXCEPTIONAL_SEED = "4619122171158768524"
DEFAULT_JACOBIAN_STEPS = "1e-3,3e-4,1e-4,3e-5,1e-5,3e-6,1e-6"
DEFAULT_MAX_SEEDS = 0
DEFAULT_BOUNDARY_TOL = 1e-9
DEFAULT_MIN_STEP_FRACTION = 0.5
DEFAULT_MIN_AMPLITUDE_FRACTION = 0.9
DEFAULT_MIN_RELATIVE_AMPLITUDE = 1e-6
DEFAULT_TYPICAL_RATE = 0.3157894736842105
DEFAULT_SLOW_CUTOFF = 0.25
DEFAULT_EXCEPTIONAL_CHECK_TIMES = "120"
DEFAULT_TRANSIENT_TIME = 15.0
DEFAULT_TRANSIENT_SAMPLES = 151
ZERO_TOL = 1e-14


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_float_list(value: str) -> list[float]:
    try:
        result = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated floats") from exc
    if not result or any(item <= 0.0 for item in result):
        raise argparse.ArgumentTypeError("all values must be positive")
    return sorted(set(result), reverse=True)


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
    return scalar, tangent, manifest


def mask_hash(mask: np.ndarray) -> str:
    packed = np.packbits(np.asarray(mask, dtype=np.uint8))
    return hashlib.sha256(packed.tobytes()).hexdigest()[:16]


def tangent_basis(
    w: np.ndarray,
    A: np.ndarray,
    saturated: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float]:
    support = np.flatnonzero(w > ZERO_TOL)
    active_nodes = np.flatnonzero(saturated)
    if not len(support):
        return np.zeros((len(w), 0)), support, 0.0
    matrix = A[np.ix_(active_nodes, support)]
    if matrix.size == 0:
        support_basis = np.eye(len(support))
        null_residual = 0.0
    else:
        _, singular_values, vh = np.linalg.svd(matrix, full_matrices=True)
        rank = int(np.sum(singular_values > 1e-10))
        support_basis = vh[rank:].T
        null_residual = float(np.linalg.norm(matrix @ support_basis))
    basis = np.zeros((len(w), support_basis.shape[1]))
    basis[support, :] = support_basis
    return basis, support, null_residual


def face_components(
    state: base.DynamicState,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
) -> dict[str, Any]:
    components = previous_analysis.state_field_components(
        state, model, capacities, A, edges, boundary_tolerance
    )
    w = components["w"]
    alpha = components["alpha"]
    support = w > ZERO_TOL
    saturated = components["saturated"]
    outward = saturated & (components["d"] > 0.0)

    endpoint_rate = np.zeros(len(w), dtype=float)
    controller = np.full(len(w), -1, dtype=int)
    tie = np.zeros(len(w), dtype=bool)
    for edge, (node_i, node_j) in enumerate(zip(edges[0], edges[1])):
        ai = alpha[node_i]
        aj = alpha[node_j]
        endpoint_rate[edge] = max(ai, aj)
        if abs(ai - aj) <= 1e-12:
            tie[edge] = True
            controller[edge] = min(node_i, node_j)
        else:
            controller[edge] = node_i if ai > aj else node_j

    basis, support_indices, null_residual = tangent_basis(w, A, saturated)
    positive_rates = np.round(endpoint_rate[support], 12)
    positive_node_degrees = sorted(
        (A[:, support] @ np.ones(np.sum(support))).astype(int).tolist()
    )
    controller_counts = sorted(
        np.bincount(
            controller[support], minlength=A.shape[0]
        ).astype(int).tolist()
    )
    geometry_signature = {
        "support_size": int(np.sum(support)),
        "saturated_count": int(np.sum(saturated)),
        "outward_count": int(np.sum(outward)),
        "tangent_dimension": int(basis.shape[1]),
        "positive_node_degrees": positive_node_degrees,
        "controller_edge_counts": controller_counts,
        "controller_tie_count": int(np.sum(tie & support)),
    }
    # The augmented signature deliberately includes continuous equilibrium
    # correction rates. It must not be used to claim geometry-only prediction.
    augmented_signature = {
        **geometry_signature,
        "positive_endpoint_rates": sorted(positive_rates.tolist()),
    }
    geometry_text = json.dumps(geometry_signature, sort_keys=True)
    augmented_text = json.dumps(augmented_signature, sort_keys=True)

    return {
        **components,
        "support": support,
        "outward": outward,
        "endpoint_rate": endpoint_rate,
        "controller": controller,
        "controller_tie": tie,
        "basis": basis,
        "support_indices": support_indices,
        "nullspace_residual": null_residual,
        "support_hash": mask_hash(support),
        "saturated_hash": mask_hash(saturated),
        "outward_hash": mask_hash(outward),
        "controller_hash": hashlib.sha256(
            controller[support].astype(np.int16).tobytes()
        ).hexdigest()[:16],
        "face_hash": hashlib.sha256(
            (
                mask_hash(support)
                + mask_hash(saturated)
                + mask_hash(outward)
                + hashlib.sha256(
                    controller[support].astype(np.int16).tobytes()
                ).hexdigest()[:16]
            ).encode()
        ).hexdigest()[:16],
        "geometry_signature": geometry_text,
        "geometry_invariant_hash": hashlib.sha256(
            geometry_text.encode()
        ).hexdigest()[:16],
        "augmented_signature": augmented_text,
        "augmented_invariant_hash": hashlib.sha256(
            augmented_text.encode()
        ).hexdigest()[:16],
        # Backwards-compatible aliases; these refer to the augmented signature.
        "invariant_signature": augmented_text,
        "invariant_hash": hashlib.sha256(
            augmented_text.encode()
        ).hexdigest()[:16],
    }


def analytic_tangent_jacobian(
    components: dict[str, Any],
    gamma: float,
) -> np.ndarray:
    basis = components["basis"]
    diagonal = -(gamma + components["endpoint_rate"])
    return basis.T @ np.diag(diagonal) @ basis


def field_at_state(
    state: base.DynamicState,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
) -> tuple[np.ndarray, dict[str, Any]]:
    components = face_components(
        state, model, capacities, A, edges, boundary_tolerance
    )
    return components["field"], components


def jacobian_structure_metrics(J: np.ndarray, gamma: float) -> dict[str, float]:
    dimension = J.shape[0]
    if dimension == 0:
        return {
            "mean_contraction_rate": np.nan,
            "scalar_isotropy_relative_error": np.nan,
            "real_eigenvalue_spread": np.nan,
            "admissibility_contribution_norm": 0.0,
            "admissibility_contribution_spectral_abscissa": np.nan,
        }
    kappa = -float(np.trace(J)) / dimension
    scalar_reference = -kappa * np.eye(dimension)
    isotropy_error = float(
        np.linalg.norm(J - scalar_reference)
        / max(np.linalg.norm(J), ZERO_TOL)
    )
    eigenvalues = np.linalg.eigvals(J)
    contribution = J + gamma * np.eye(dimension)
    contribution_values = np.linalg.eigvals(contribution)
    return {
        "mean_contraction_rate": kappa,
        "scalar_isotropy_relative_error": isotropy_error,
        "real_eigenvalue_spread": float(
            np.max(np.real(eigenvalues)) - np.min(np.real(eigenvalues))
        ),
        "admissibility_contribution_norm": float(np.linalg.norm(contribution)),
        "admissibility_contribution_spectral_abscissa": float(
            np.max(np.real(contribution_values))
        ),
    }


def numerical_tangent_jacobian(
    state: base.DynamicState,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    relative_step: float,
    minimum_step_fraction: float,
) -> tuple[np.ndarray | None, dict[str, Any], list[dict[str, Any]]]:
    base_components = face_components(
        state, model, capacities, A, edges, boundary_tolerance
    )
    w = base_components["w"]
    basis = base_components["basis"]
    dimension = basis.shape[1]
    if dimension == 0:
        return None, {"status": "empty_tangent_space"}, []

    norm_w = max(float(np.linalg.norm(w)), ZERO_TOL)
    columns: list[np.ndarray] = []
    direction_rows: list[dict[str, Any]] = []

    for direction_id in range(dimension):
        direction = basis[:, direction_id]
        requested = relative_step * norm_w
        plus_limit = base.maximum_feasible_amplitude(w, direction, A, capacities)
        minus_limit = base.maximum_feasible_amplitude(w, -direction, A, capacities)
        actual = min(requested, 0.25 * plus_limit, 0.25 * minus_limit)
        fraction = actual / requested if requested > 0.0 else 0.0
        if (
            not np.isfinite(actual)
            or actual <= 1e-12 * norm_w
            or fraction < minimum_step_fraction
        ):
            return None, {
                "status": "insufficient_two_sided_step",
                "failed_direction": direction_id,
                "requested_step": requested,
                "actual_step": actual,
                "step_fraction": fraction,
            }, direction_rows

        fields = []
        stratum_preserved = True
        for sign in (1.0, -1.0):
            perturbed = w + sign * actual * direction
            perturbed_state = state.clone()
            perturbed_state.B = base.vector_to_matrix(
                perturbed, state.B.shape[0], edges
            )
            field, components = field_at_state(
                perturbed_state,
                model,
                capacities,
                A,
                edges,
                boundary_tolerance,
            )
            fields.append(field)
            stratum_preserved &= bool(
                components["support_hash"] == base_components["support_hash"]
                and components["saturated_hash"]
                == base_components["saturated_hash"]
                and components["outward_hash"] == base_components["outward_hash"]
                and components["controller_hash"]
                == base_components["controller_hash"]
            )

        derivative = (fields[0] - fields[1]) / (2.0 * actual)
        tangent_column = basis.T @ derivative
        normal_leakage = float(
            np.linalg.norm(derivative - basis @ tangent_column)
        )
        columns.append(tangent_column)
        direction_rows.append(
            {
                "direction_id": direction_id,
                "requested_step": requested,
                "actual_step": actual,
                "step_fraction": fraction,
                "stratum_preserved": stratum_preserved,
                "derivative_norm": float(np.linalg.norm(derivative)),
                "normal_leakage_norm": normal_leakage,
            }
        )

    J = np.column_stack(columns)
    return J, {
        "status": "ok",
        "tangent_dimension": dimension,
        "all_directions_preserved_stratum": bool(
            all(row["stratum_preserved"] for row in direction_rows)
        ),
        "max_normal_leakage": float(
            max(row["normal_leakage_norm"] for row in direction_rows)
        ),
    }, direction_rows


def matrix_spectral_summary(J: np.ndarray) -> dict[str, float]:
    eigenvalues, eigenvectors = np.linalg.eig(J)
    symmetric = 0.5 * (J + J.T)
    symmetric_eigenvalues = np.linalg.eigvalsh(symmetric)
    singular_values = np.linalg.svd(J, compute_uv=False)
    commutator = J.T @ J - J @ J.T
    return {
        "spectral_abscissa": float(np.max(np.real(eigenvalues))),
        "slowest_decay_rate": float(-np.max(np.real(eigenvalues))),
        "minimum_real_eigenvalue": float(np.min(np.real(eigenvalues))),
        "symmetric_part_lambda_max": float(symmetric_eigenvalues[-1]),
        "symmetric_part_lambda_min": float(symmetric_eigenvalues[0]),
        "largest_singular_value": float(singular_values[0]),
        "smallest_singular_value": float(singular_values[-1]),
        "eigenvector_condition_number": float(np.linalg.cond(eigenvectors)),
        "normality_commutator_ratio": float(
            np.linalg.norm(commutator)
            / max(np.linalg.norm(J) ** 2, ZERO_TOL)
        ),
    }


def transient_amplification(
    J: np.ndarray,
    max_time: float,
    samples: int,
) -> dict[str, float]:
    eigenvalues, eigenvectors = np.linalg.eig(J)
    condition = float(np.linalg.cond(eigenvectors))
    if not np.isfinite(condition) or condition > 1e14:
        return {
            "peak_propagator_norm": np.nan,
            "peak_propagator_time": np.nan,
            "final_propagator_norm": np.nan,
        }
    inverse = np.linalg.inv(eigenvectors)
    peak = -np.inf
    peak_time = np.nan
    final_norm = np.nan
    for time_value in np.linspace(0.0, max_time, samples):
        propagator = (
            eigenvectors
            @ np.diag(np.exp(eigenvalues * time_value))
            @ inverse
        )
        norm = float(np.linalg.norm(propagator, ord=2))
        if norm > peak:
            peak = norm
            peak_time = float(time_value)
        final_norm = norm
    return {
        "peak_propagator_norm": float(peak),
        "peak_propagator_time": peak_time,
        "final_propagator_norm": float(final_norm),
    }


def match_eigenvalues(
    analytic: np.ndarray,
    numerical: np.ndarray,
) -> dict[str, float]:
    analytic_values = np.linalg.eigvals(analytic)
    numerical_values = np.linalg.eigvals(numerical)
    unmatched = list(numerical_values)
    errors = []
    for value in analytic_values:
        index = int(np.argmin([abs(value - candidate) for candidate in unmatched]))
        errors.append(abs(value - unmatched.pop(index)))
    return {
        "eigenvalue_match_max_error": float(max(errors)) if errors else np.nan,
        "eigenvalue_match_mean_error": float(np.mean(errors)) if errors else np.nan,
    }


def exceptional_states(
    data: Any,
    seed: str,
    manifest: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    checkpoint_times: Iterable[float],
) -> tuple[dict[str, base.DynamicState], dict[str, Any]]:
    model = manifest["model"]
    future_steps = int(manifest["protocol"]["future_steps"])
    state = base.load_split_state(data, seed)
    stages: dict[str, base.DynamicState] = {"split": state.clone()}
    dt = float(model["dt"])
    checkpoint_steps = {
        int(round(time_value / dt)): time_value
        for time_value in checkpoint_times
    }
    previous_saturated: np.ndarray | None = None
    previous_state: base.DynamicState | None = None
    switch_step = None

    for step in range(future_steps):
        if step in checkpoint_steps:
            label = f"time_{checkpoint_steps[step]:g}".replace(".", "p")
            stages[label] = state.clone()
        components = face_components(
            state, model, capacities, A, edges, boundary_tolerance
        )
        saturated = components["saturated"]
        if (
            previous_saturated is not None
            and not np.array_equal(saturated, previous_saturated)
            and switch_step is None
        ):
            switch_step = step
            if previous_state is not None:
                stages["pre_switch"] = previous_state.clone()
            stages["post_switch"] = state.clone()
        previous_saturated = saturated.copy()
        previous_state = state.clone()
        base.actual_step(
            state,
            model,
            capacities,
            A,
            edges,
            boundary_tolerance,
            audit_operator=False,
        )
    stages["late"] = state.clone()
    return stages, {
        "switch_step": switch_step,
        "requested_checkpoint_times": list(checkpoint_times),
        "captured_stages": sorted(stages),
        "switch_time": (switch_step + 1) * float(model["dt"])
        if switch_step is not None
        else np.nan,
    }


def tangent_rate_cross_tab(
    direction_summary: pd.DataFrame,
    fingerprints: pd.DataFrame,
    typical_rate: float,
    slow_cutoff: float,
) -> pd.DataFrame:
    merged = direction_summary.merge(
        fingerprints[
            [
                "seed",
                "face_hash",
                "invariant_hash",
                "geometry_invariant_hash",
                "augmented_invariant_hash",
                "tangent_dimension",
                "support_size",
                "saturated_count",
                "outward_count",
                "analytic_spectral_abscissa",
                "analytic_slowest_decay_rate",
            ]
        ],
        on="seed",
        how="left",
    )
    merged["observed_rate_class"] = np.select(
        [
            ~merged["amplitude_reliable"],
            merged["observed_rate_median"] < slow_cutoff,
            np.abs(merged["observed_rate_median"] - typical_rate)
            / typical_rate
            <= 0.05,
        ],
        ["amplitude_unreliable", "slow", "typical"],
        default="other",
    )
    return merged


def summarize_cross_tab(merged: pd.DataFrame) -> pd.DataFrame:
    return (
        merged.groupby(
            [
                "geometry_invariant_hash",
                "augmented_invariant_hash",
                "face_hash",
                "tangent_dimension",
                "analytic_slowest_decay_rate",
                "observed_rate_class",
            ],
            dropna=False,
        )
        .agg(
            direction_count=("direction_id", "count"),
            seed_count=("seed", "nunique"),
            observed_rate_mean=("observed_rate_median", "mean"),
            observed_rate_std=("observed_rate_median", "std"),
            frozen_rate_mean=("frozen_rate_median", "mean"),
            reliable_fraction=("amplitude_reliable", "mean"),
        )
        .reset_index()
    )


def fingerprint_spectrum_consistency(
    fingerprints: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for signature_type, column in (
        ("geometry_only", "geometry_invariant_hash"),
        ("geometry_plus_rates", "augmented_invariant_hash"),
        ("labeled_face", "face_hash"),
    ):
        for signature, group in fingerprints.groupby(column, dropna=False):
            rates = group["analytic_slowest_decay_rate"].to_numpy(float)
            isotropy = group["analytic_scalar_isotropy_relative_error"].to_numpy(float)
            rows.append(
                {
                    "signature_type": signature_type,
                    "signature": signature,
                    "seed_count": int(len(group)),
                    "tangent_dimension_count": int(
                        group["tangent_dimension"].nunique()
                    ),
                    "rate_mean": float(np.mean(rates)),
                    "rate_std": float(np.std(rates)),
                    "rate_min": float(np.min(rates)),
                    "rate_max": float(np.max(rates)),
                    "rate_range": float(np.max(rates) - np.min(rates)),
                    "isotropy_error_median": float(np.median(isotropy)),
                    "isotropy_error_max": float(np.max(isotropy)),
                    "same_rate_1e10": bool(
                        np.max(rates) - np.min(rates) <= 1e-10
                    ),
                }
            )
    return pd.DataFrame(rows)


def make_report(
    fingerprints: pd.DataFrame,
    fingerprint_consistency: pd.DataFrame,
    jacobian_summary: pd.DataFrame,
    cross_tab: pd.DataFrame,
    exceptional_summary: dict[str, Any],
) -> str:
    lines = [
        "AIEF active-face spectrum and exceptional transition analysis",
        "=============================================================",
        "",
        f"Seeds with fingerprints: {len(fingerprints)}",
        f"Distinct labeled face hashes: {fingerprints['face_hash'].nunique()}",
        f"Distinct invariant signatures: {fingerprints['invariant_hash'].nunique()}",
        "",
        "Analytic fixed-stratum spectral classes",
        "---------------------------------------",
    ]
    grouped = fingerprints.groupby(
        ["tangent_dimension", "analytic_slowest_decay_rate"]
    ).size().reset_index(name="seed_count")
    for _, row in grouped.iterrows():
        lines.append(
            f"  dimension={int(row['tangent_dimension'])}, "
            f"rate={row['analytic_slowest_decay_rate']:.12g}, "
            f"seeds={int(row['seed_count'])}"
        )

    lines.extend(["", "Fingerprint-to-spectrum consistency", "-----------------------------------"])
    repeated = fingerprint_consistency.loc[
        fingerprint_consistency["seed_count"] >= 2
    ]
    for _, row in repeated.iterrows():
        lines.append(
            f"  {row['signature_type']} {row['signature']}: "
            f"seeds={int(row['seed_count'])}, "
            f"rate_range={row['rate_range']:.6g}, "
            f"same_rate_1e10={row['same_rate_1e10']}"
        )
    if repeated.empty:
        lines.append("  no repeated fingerprint groups")

    lines.extend(["", "Numerical/analytic Jacobian agreement", "-------------------------------------"])
    successful = jacobian_summary.loc[jacobian_summary["status"] == "ok"]
    for step, group in successful.groupby("relative_step"):
        lines.append(
            f"  step={step:g}: matrix relative error median="
            f"{group['matrix_relative_error'].median():.6g}, "
            f"eigenvalue max error median="
            f"{group['eigenvalue_match_max_error'].median():.6g}, "
            f"stratum preserved={group['all_directions_preserved_stratum'].mean():.3f}"
        )

    lines.extend(["", "Exceptional transition", "----------------------"])
    for key, value in exceptional_summary.items():
        lines.append(f"  {key}: {value}")

    lines.extend(["", "Face/rate cross-tab", "-------------------"])
    for _, row in cross_tab.iterrows():
        lines.append(
            f"  geom={row['geometry_invariant_hash']}, "
            f"aug={row['augmented_invariant_hash']}, "
            f"dim={row['tangent_dimension']}, "
            f"analytic_rate={row['analytic_slowest_decay_rate']}, "
            f"class={row['observed_rate_class']}, "
            f"directions={int(row['direction_count'])}, seeds={int(row['seed_count'])}, "
            f"observed_mean={row['observed_rate_mean']:.6g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* A face class includes support, saturation, outward set, endpoint controllers, and equilibrium rates.",
            "* Repeated rational-looking rates must be derived from gamma, alpha, incidence, and weights before being called quantized.",
            "* The exceptional split Jacobian is not a stationary-face Jacobian; pre/post/late stages are reported separately.",
            "* Negative spectral abscissa is frozen-fast local evidence, not full coupled stability.",
            "* B_carrier_only/full_reset phase matching is unrelated to this analysis.",
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
        "--exceptional-check-times",
        type=base.parse_float_list,
        default=base.parse_float_list(DEFAULT_EXCEPTIONAL_CHECK_TIMES),
        help="comma-separated times since split for exceptional-stage spectra",
    )
    parser.add_argument(
        "--jacobian-steps",
        type=base.parse_float_list,
        default=base.parse_float_list(DEFAULT_JACOBIAN_STEPS),
    )
    parser.add_argument("--max-seeds", type=int, default=DEFAULT_MAX_SEEDS)
    parser.add_argument("--boundary-tol", type=float, default=DEFAULT_BOUNDARY_TOL)
    parser.add_argument(
        "--min-step-fraction", type=float, default=DEFAULT_MIN_STEP_FRACTION
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
    parser.add_argument("--typical-rate", type=float, default=DEFAULT_TYPICAL_RATE)
    parser.add_argument("--slow-cutoff", type=float, default=DEFAULT_SLOW_CUTOFF)
    parser.add_argument(
        "--transient-time", type=float, default=DEFAULT_TRANSIENT_TIME
    )
    parser.add_argument(
        "--transient-samples", type=int, default=DEFAULT_TRANSIENT_SAMPLES
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.scalar, args.npz, args.manifest, args.tangent_results):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if (
        args.max_seeds < 0
        or args.boundary_tol < 0.0
        or not 0.0 < args.min_step_fraction <= 1.0
        or args.transient_time <= 0.0
        or args.transient_samples < 2
    ):
        raise ValueError("invalid command-line settings")
    os.makedirs(args.output_dir, exist_ok=True)

    scalar, tangent, manifest = load_inputs(
        args.scalar, args.tangent_results, args.manifest
    )
    direction_summary, anomalous, agreement = (
        previous_analysis.tangent_direction_summary(
            tangent,
            args.min_amplitude_fraction,
            args.min_relative_amplitude,
            args.typical_rate,
            args.slow_cutoff,
        )
    )

    model = manifest["model"]
    node_count = int(model["N"])
    gamma = float(model["gamma"])
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(node_count, capacity)
    A, edges = base.incidence_matrix(node_count)
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )
    selected_seeds = seeds if args.max_seeds == 0 else seeds[: args.max_seeds]

    fingerprint_rows: list[dict[str, Any]] = []
    jacobian_rows: list[dict[str, Any]] = []
    eigen_rows: list[dict[str, Any]] = []
    direction_rows: list[dict[str, Any]] = []
    jacobian_payload: dict[str, np.ndarray] = {}

    with np.load(args.npz, allow_pickle=False) as data:
        for seed in seeds:
            state = base.load_split_state(data, seed)
            components = face_components(
                state, model, capacities, A, edges, args.boundary_tol
            )
            analytic_J = analytic_tangent_jacobian(components, gamma)
            analytic_spec = matrix_spectral_summary(analytic_J)
            analytic_structure = jacobian_structure_metrics(analytic_J, gamma)
            analytic_transient = transient_amplification(
                analytic_J, args.transient_time, args.transient_samples
            )
            fingerprint_rows.append(
                {
                    "seed": seed,
                    "face_hash": components["face_hash"],
                    "invariant_hash": components["invariant_hash"],
                    "invariant_signature": components["invariant_signature"],
                    "geometry_invariant_hash": components[
                        "geometry_invariant_hash"
                    ],
                    "geometry_signature": components["geometry_signature"],
                    "augmented_invariant_hash": components[
                        "augmented_invariant_hash"
                    ],
                    "augmented_signature": components["augmented_signature"],
                    "support_hash": components["support_hash"],
                    "saturated_hash": components["saturated_hash"],
                    "outward_hash": components["outward_hash"],
                    "controller_hash": components["controller_hash"],
                    "support_size": int(np.sum(components["support"])),
                    "saturated_count": int(np.sum(components["saturated"])),
                    "outward_count": int(np.sum(components["outward"])),
                    "controller_tie_count": int(
                        np.sum(components["controller_tie"] & components["support"])
                    ),
                    "tangent_dimension": int(components["basis"].shape[1]),
                    "nullspace_residual": components["nullspace_residual"],
                    **{
                        f"analytic_{key}": value
                        for key, value in {
                            **analytic_spec,
                            **analytic_structure,
                            **analytic_transient,
                        }.items()
                    },
                }
            )

            if seed in selected_seeds:
                for relative_step in args.jacobian_steps:
                    numerical_J, status, details = numerical_tangent_jacobian(
                        state,
                        model,
                        capacities,
                        A,
                        edges,
                        args.boundary_tol,
                        relative_step,
                        args.min_step_fraction,
                    )
                    row: dict[str, Any] = {
                        "seed": seed,
                        "relative_step": relative_step,
                        "face_hash": components["face_hash"],
                        "invariant_hash": components["invariant_hash"],
                        "geometry_invariant_hash": components[
                            "geometry_invariant_hash"
                        ],
                        "augmented_invariant_hash": components[
                            "augmented_invariant_hash"
                        ],
                        **status,
                    }
                    if numerical_J is not None:
                        numerical_spec = matrix_spectral_summary(numerical_J)
                        numerical_structure = jacobian_structure_metrics(
                            numerical_J, gamma
                        )
                        match = match_eigenvalues(analytic_J, numerical_J)
                        row.update(
                            {
                                **{
                                    f"numerical_{key}": value
                                    for key, value in {
                                        **numerical_spec,
                                        **numerical_structure,
                                    }.items()
                                },
                                **match,
                                "matrix_absolute_error": float(
                                    np.linalg.norm(numerical_J - analytic_J)
                                ),
                                "matrix_relative_error": float(
                                    np.linalg.norm(numerical_J - analytic_J)
                                    / max(np.linalg.norm(analytic_J), ZERO_TOL)
                                ),
                            }
                        )
                        jacobian_payload[
                            f"seed_{seed}_step_{relative_step:g}_numerical"
                        ] = numerical_J
                    jacobian_payload[f"seed_{seed}_analytic"] = analytic_J
                    jacobian_rows.append(row)
                    for detail in details:
                        direction_rows.append(
                            {
                                "seed": seed,
                                "relative_step": relative_step,
                                **detail,
                            }
                        )

        exceptional_stage_states, exceptional_summary = exceptional_states(
            data,
            args.exceptional_seed,
            manifest,
            capacities,
            A,
            edges,
            args.boundary_tol,
            args.exceptional_check_times,
        )
        exceptional_rows: list[dict[str, Any]] = []
        for stage, state in exceptional_stage_states.items():
            components = face_components(
                state, model, capacities, A, edges, args.boundary_tol
            )
            analytic_J = analytic_tangent_jacobian(components, gamma)
            analytic_spec = matrix_spectral_summary(analytic_J)
            analytic_structure = jacobian_structure_metrics(analytic_J, gamma)
            analytic_transient = transient_amplification(
                analytic_J, args.transient_time, args.transient_samples
            )
            exceptional_rows.append(
                {
                    "seed": args.exceptional_seed,
                    "stage": stage,
                    "face_hash": components["face_hash"],
                    "invariant_hash": components["invariant_hash"],
                    "geometry_invariant_hash": components[
                        "geometry_invariant_hash"
                    ],
                    "augmented_invariant_hash": components[
                        "augmented_invariant_hash"
                    ],
                    "support_size": int(np.sum(components["support"])),
                    "saturated_count": int(np.sum(components["saturated"])),
                    "outward_count": int(np.sum(components["outward"])),
                    "tangent_dimension": int(components["basis"].shape[1]),
                    "field_norm": float(np.linalg.norm(components["field"])),
                    **analytic_spec,
                    **analytic_structure,
                    **analytic_transient,
                }
            )
            jacobian_payload[f"exceptional_{stage}_analytic"] = analytic_J

    fingerprints = pd.DataFrame(fingerprint_rows)
    fingerprint_consistency = fingerprint_spectrum_consistency(fingerprints)
    jacobian_summary = pd.DataFrame(jacobian_rows)
    jacobian_details = pd.DataFrame(direction_rows)
    exceptional_spectra = pd.DataFrame(exceptional_rows)
    cross_tab_rows = tangent_rate_cross_tab(
        direction_summary,
        fingerprints,
        args.typical_rate,
        args.slow_cutoff,
    )
    cross_tab_summary = summarize_cross_tab(cross_tab_rows)

    # Long-format eigenvalue table for analytic and numerical matrices.
    for key, matrix in jacobian_payload.items():
        eigenvalues = np.linalg.eigvals(matrix)
        for mode, value in enumerate(eigenvalues):
            eigen_rows.append(
                {
                    "matrix_key": key,
                    "mode": mode,
                    "eigenvalue_real": float(np.real(value)),
                    "eigenvalue_imag": float(np.imag(value)),
                }
            )
    eigen_frame = pd.DataFrame(eigen_rows)

    outputs = {
        "active_face_fingerprints.csv": fingerprints,
        "fingerprint_spectrum_consistency.csv": fingerprint_consistency,
        "tangent_direction_summary.csv": direction_summary,
        "filtered_anomalous_directions.csv": anomalous,
        "tangent_rate_face_crosstab_rows.csv": cross_tab_rows,
        "tangent_rate_face_crosstab_summary.csv": cross_tab_summary,
        "jacobian_step_sensitivity.csv": jacobian_summary,
        "jacobian_direction_diagnostics.csv": jacobian_details,
        "jacobian_eigenvalues.csv": eigen_frame,
        "exceptional_stage_spectra.csv": exceptional_spectra,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(args.output_dir, filename), index=False)
    np.savez_compressed(
        os.path.join(args.output_dir, "tangent_jacobian_matrices.npz"),
        **jacobian_payload,
    )

    with open(
        os.path.join(args.output_dir, "direction_agreement_summary.json"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(agreement, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(
        os.path.join(args.output_dir, "exceptional_transition_summary.json"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(exceptional_summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    report = make_report(
        fingerprints,
        fingerprint_consistency,
        jacobian_summary,
        cross_tab_summary,
        exceptional_summary,
    )
    with open(
        os.path.join(args.output_dir, "face_spectrum_report.txt"),
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(report)
    print(report)

    analysis_manifest = {
        "analysis": "AIEF fixed-face spectrum and exceptional transition",
        "scalar_path": str(Path(args.scalar).resolve()),
        "scalar_sha256": file_sha256(args.scalar),
        "npz_path": str(Path(args.npz).resolve()),
        "npz_sha256": file_sha256(args.npz),
        "source_manifest_path": str(Path(args.manifest).resolve()),
        "source_manifest_sha256": file_sha256(args.manifest),
        "tangent_results_path": str(Path(args.tangent_results).resolve()),
        "tangent_results_sha256": file_sha256(args.tangent_results),
        "exceptional_seed": args.exceptional_seed,
        "exceptional_check_times": args.exceptional_check_times,
        "jacobian_steps": args.jacobian_steps,
        "selected_jacobian_seeds": selected_seeds,
        "boundary_tolerance": args.boundary_tol,
        "minimum_step_fraction": args.min_step_fraction,
        "minimum_amplitude_fraction": args.min_amplitude_fraction,
        "minimum_relative_amplitude": args.min_relative_amplitude,
        "typical_rate": args.typical_rate,
        "slow_cutoff": args.slow_cutoff,
        "transient_time": args.transient_time,
        "transient_samples": args.transient_samples,
        "analytic_jacobian": "Q_T^T diag(-gamma-max(alpha_i,alpha_j)) Q_T",
        "notes": [
            "Analytic formula assumes fixed support, saturated/outward sets, and endpoint controllers.",
            "Exceptional split Jacobian is not assumed to be stationary.",
            "Face quantization is a hypothesis tested by fingerprint/spectrum cross-tabs.",
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
