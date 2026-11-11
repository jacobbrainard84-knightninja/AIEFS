#!/usr/bin/env python3
"""Intertwining and mature controller-equilibrium analysis for AIEF-1.4.

The script tests the algebraic mechanism behind tangent-channel invariance.
For each mature split state it constructs

    C = A[saturated_nodes, positive_edges]
    D = diag(-gamma - rho_e)

and finds the least-squares node-space operator L satisfying

    C D ~= L C.

It also constructs the endpoint-controller matrix K and tests the mature
balance relation

    diag(c) alpha ~= K alpha.

Finally, it replays the exceptional seed around its saturated-set switch and
tracks the intertwining residual, channel commutator, tangent dimension, and
controller-equilibrium residual at every nearby step.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import AIEF_1_4_stationarity_perturbation_analysis_updated as base
import AIEF_1_4_face_spectrum_analysis as face
import AIEF_1_4_tangent_spectrum_switch_analysis as tangent_analysis


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
DEFAULT_MODAL_SUMMARY = (
    "aief_1_4_face_spectrum/modal_trajectory_prediction_summary.csv"
)
DEFAULT_OUTPUT_DIR = "aief_1_4_intertwining_controller"
DEFAULT_EXCEPTIONAL_SEED = "4619122171158768524"
DEFAULT_EXCEPTIONAL_CHECK_TIMES = "100,120,123,125,150"
DEFAULT_BOUNDARY_TOL = 1e-9
DEFAULT_SPECTRUM_TOL = 1e-10
DEFAULT_CHANNEL_TOL = 1e-10
DEFAULT_SUBSPACE_TOL = 1e-9
DEFAULT_MODAL_R2 = 0.95
ZERO_TOL = 1e-14


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def spectrum_vector(J: np.ndarray) -> np.ndarray:
    return np.sort(np.real(np.linalg.eigvals(J)))


def cluster_values(values: np.ndarray, tolerance: float) -> list[np.ndarray]:
    values = np.sort(np.asarray(values, dtype=float))
    if not len(values):
        return []
    clusters: list[list[float]] = [[float(values[0])]]
    for value in values[1:]:
        if abs(float(value) - np.mean(clusters[-1])) <= tolerance:
            clusters[-1].append(float(value))
        else:
            clusters.append([float(value)])
    return [np.asarray(cluster) for cluster in clusters]


def matrix_json(matrix: np.ndarray, decimals: int = 12) -> str:
    return json.dumps(
        np.round(np.asarray(matrix, dtype=float), decimals).tolist(),
        separators=(",", ":"),
    )


def channel_and_intertwining(
    state: base.DynamicState,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    channel_tolerance: float,
    subspace_tolerance: float,
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, np.ndarray],
]:
    components = face.face_components(
        state, model, capacities, A, edges, boundary_tolerance
    )
    gamma = float(model["gamma"])
    w = components["w"]
    support = components["support"]
    support_indices = np.flatnonzero(support)
    saturated_indices = np.flatnonzero(components["saturated"])
    Q = components["basis"]
    rates_all = gamma + components["endpoint_rate"]
    rates = rates_all[support_indices]

    C = A[np.ix_(saturated_indices, support_indices)]
    D = -np.diag(rates)
    if C.size:
        C_pinv = np.linalg.pinv(C, rcond=1e-12)
        L = (C @ D) @ C_pinv
        residual = C @ D - L @ C
        residual_relative = float(
            np.linalg.norm(residual) / max(np.linalg.norm(C @ D), ZERO_TOL)
        )
        row_projector = C_pinv @ C
        rowspace_residual = float(
            np.linalg.norm((C @ D) @ (np.eye(len(rates)) - row_projector))
            / max(np.linalg.norm(C @ D), ZERO_TOL)
        )
        C_rank = int(np.linalg.matrix_rank(C, tol=1e-10))
    else:
        C_pinv = np.zeros((len(rates), 0))
        L = np.zeros((0, 0))
        residual_relative = rowspace_residual = 0.0
        C_rank = 0

    P_T = Q @ Q.T
    D_full = np.diag(-rates_all)
    commutator = D_full @ P_T - P_T @ D_full
    commutator_relative = float(
        np.linalg.norm(commutator) / max(np.linalg.norm(D_full), ZERO_TOL)
    )

    # Endpoint-controller equilibrium matrix K:
    # c_i alpha_i = sum_{e incident i} w_e alpha_controller(e).
    node_count = len(capacities)
    K = np.zeros((node_count, node_count), dtype=float)
    for edge in support_indices:
        i = int(edges[0][edge])
        j = int(edges[1][edge])
        controller = int(components["controller"][edge])
        K[i, controller] += w[edge]
        K[j, controller] += w[edge]

    alpha = components["alpha"]
    controller_residual = capacities * alpha - K @ alpha
    controller_relative = float(
        np.linalg.norm(controller_residual)
        / max(np.linalg.norm(capacities * alpha), ZERO_TOL)
    )
    M = np.diag(1.0 / capacities) @ K
    M_eigenvalues = np.linalg.eigvals(M)
    nearest_one = float(
        np.min(np.abs(M_eigenvalues - 1.0))
    ) if len(M_eigenvalues) else np.nan

    # Direct edge stationarity relation on the mature support.
    modified_F = components["modified_F"]
    edge_balance = modified_F - w * components["endpoint_rate"]
    support_balance = edge_balance[support]
    edge_balance_relative = float(
        np.linalg.norm(support_balance)
        / max(np.linalg.norm(modified_F[support]), ZERO_TOL)
    )
    zero_edge_forcing_violation = float(
        np.max(np.maximum(modified_F[~support], 0.0))
    ) if np.any(~support) else 0.0

    channel_rows: list[dict[str, Any]] = []
    clusters = cluster_values(rates, channel_tolerance)
    predicted_total = 0
    for channel_id, cluster in enumerate(clusters):
        representative = float(np.mean(cluster))
        local_indices = np.flatnonzero(
            np.abs(rates - representative) <= channel_tolerance
        )
        global_indices = support_indices[local_indices]
        outside = np.setdiff1d(
            np.arange(Q.shape[0]), global_indices, assume_unique=True
        )
        if len(outside):
            singular_values = np.linalg.svd(Q[outside, :], compute_uv=False)
            intersection = int(
                Q.shape[1] - np.sum(singular_values > subspace_tolerance)
            )
        else:
            intersection = int(Q.shape[1])
        predicted_total += intersection
        J = face.analytic_tangent_jacobian(components, gamma)
        eigenvalues = np.sort(-np.real(np.linalg.eigvals(J)))
        observed = int(
            np.sum(np.abs(eigenvalues - representative) <= channel_tolerance)
        )
        channel_rows.append(
            {
                "channel_id": channel_id,
                "contraction_rate": representative,
                "rho_value": representative - gamma,
                "edge_count": int(len(global_indices)),
                "intersection_dimension": intersection,
                "observed_eigenvalue_multiplicity": observed,
                "multiplicity_matches": bool(intersection == observed),
                "edge_indices": ";".join(map(str, global_indices.tolist())),
            }
        )

    node_rows: list[dict[str, Any]] = []
    positive_degree = A[:, support] @ np.ones(np.sum(support))
    controller_count = np.bincount(
        components["controller"][support], minlength=node_count
    )
    for node in range(node_count):
        node_rows.append(
            {
                "node": node,
                "saturated": bool(components["saturated"][node]),
                "outward": bool(components["outward"][node]),
                "row_sum": float(A[node] @ w),
                "slack": float(capacities[node] - A[node] @ w),
                "row_direction_d": float(components["d"][node]),
                "alpha": float(alpha[node]),
                "positive_support_degree": int(positive_degree[node]),
                "controller_edge_count": int(controller_count[node]),
                "controller_equation_residual": float(controller_residual[node]),
            }
        )

    J = face.analytic_tangent_jacobian(components, gamma)
    J_eigenvalues = np.sort(np.real(np.linalg.eigvals(J)))
    summary = {
        "face_hash": components["face_hash"],
        "geometry_invariant_hash": components["geometry_invariant_hash"],
        "augmented_invariant_hash": components["augmented_invariant_hash"],
        "support_size": int(np.sum(support)),
        "saturated_count": int(len(saturated_indices)),
        "outward_count": int(np.sum(components["outward"])),
        "tangent_dimension": int(Q.shape[1]),
        "constraint_matrix_rank": C_rank,
        "intertwining_residual_relative": residual_relative,
        "rowspace_invariance_residual_relative": rowspace_residual,
        "tangent_commutator_relative": commutator_relative,
        "controller_equilibrium_residual_relative": controller_relative,
        "controller_eigenvalue_distance_to_one": nearest_one,
        "edge_balance_residual_relative": edge_balance_relative,
        "zero_edge_positive_forcing_violation": zero_edge_forcing_violation,
        "channel_count": int(len(clusters)),
        "predicted_multiplicity_total": int(predicted_total),
        "predicted_multiplicities_cover_tangent": bool(
            predicted_total == Q.shape[1]
        ),
        "all_channel_multiplicities_match": bool(
            all(row["multiplicity_matches"] for row in channel_rows)
        ),
        "spectrum_values_json": json.dumps(
            J_eigenvalues.tolist(), separators=(",", ":")
        ),
        "alpha_values_json": json.dumps(
            np.round(alpha, 12).tolist(), separators=(",", ":")
        ),
        "controller_matrix_eigenvalues_json": json.dumps(
            [
                [float(np.real(value)), float(np.imag(value))]
                for value in M_eigenvalues
            ],
            separators=(",", ":"),
        ),
    }
    matrices = {
        "C_active": C,
        "D_channel": D,
        "L_intertwiner": L,
        "K_controller": K,
        "P_tangent": P_T,
        "J_tangent": J,
    }
    return summary, channel_rows, node_rows, matrices


def tolerance_spectrum_consistency(
    summaries: pd.DataFrame,
    tolerance: float,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for signature_type, column in (
        ("geometry_only", "geometry_invariant_hash"),
        ("geometry_plus_rates", "augmented_invariant_hash"),
        ("labeled_face", "face_hash"),
    ):
        for signature, group in summaries.groupby(column, dropna=False):
            spectra = [
                np.asarray(json.loads(value), dtype=float)
                for value in group["spectrum_values_json"]
            ]
            maximum_error = 0.0
            for index, left in enumerate(spectra):
                for right in spectra[index + 1 :]:
                    if len(left) != len(right):
                        maximum_error = np.inf
                    else:
                        maximum_error = max(
                            maximum_error,
                            float(np.max(np.abs(np.sort(left) - np.sort(right))))
                            if len(left)
                            else 0.0,
                        )
            rows.append(
                {
                    "signature_type": signature_type,
                    "signature": signature,
                    "seed_count": int(len(group)),
                    "maximum_matched_spectrum_error": maximum_error,
                    "same_spectrum_within_tolerance": bool(
                        maximum_error <= tolerance
                    ),
                    "intertwining_residual_max": float(
                        group["intertwining_residual_relative"].max()
                    ),
                    "commutator_max": float(
                        group["tangent_commutator_relative"].max()
                    ),
                    "all_multiplicities_match": bool(
                        group["all_channel_multiplicities_match"].all()
                    ),
                }
            )
    return pd.DataFrame(rows)


def unique_direction_modal_success(
    modal_summary: pd.DataFrame,
    tangent_summary: pd.DataFrame,
    r2_threshold: float,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    modal = modal_summary.copy()
    modal["seed"] = modal["seed"].astype(str)
    rows: list[dict[str, Any]] = []
    for (seed, direction_id), group in modal.groupby(["seed", "direction_id"]):
        r2 = pd.to_numeric(
            group["trajectory_prediction_R2"], errors="coerce"
        ).to_numpy(float)
        finite = r2[np.isfinite(r2)]
        rows.append(
            {
                "seed": seed,
                "direction_id": int(direction_id),
                "amplitude_count": int(len(group)),
                "median_R2": float(np.median(finite)) if len(finite) else np.nan,
                "minimum_R2": float(np.min(finite)) if len(finite) else np.nan,
                "all_amplitudes_R2_ge_threshold": bool(
                    len(finite) == len(group)
                    and np.all(finite >= r2_threshold)
                ),
                "median_R2_ge_threshold": bool(
                    len(finite) and np.median(finite) >= r2_threshold
                ),
                "median_RMSE": float(group["rmse"].median()),
                "maximum_absolute_error": float(
                    group["maximum_absolute_error"].max()
                ),
            }
        )
    result = pd.DataFrame(rows).merge(
        tangent_summary,
        on=["seed", "direction_id"],
        how="left",
    )
    reliable = result.loc[result["amplitude_reliable"] == True]  # noqa: E712
    summary = {
        "unique_direction_count": int(len(result)),
        "reliable_unique_direction_count": int(len(reliable)),
        "all_amplitudes_success_count": int(
            result["all_amplitudes_R2_ge_threshold"].sum()
        ),
        "median_success_count": int(
            result["median_R2_ge_threshold"].sum()
        ),
        "reliable_all_amplitudes_success_fraction": float(
            reliable["all_amplitudes_R2_ge_threshold"].mean()
        )
        if len(reliable)
        else np.nan,
        "reliable_median_success_fraction": float(
            reliable["median_R2_ge_threshold"].mean()
        )
        if len(reliable)
        else np.nan,
        "median_unique_direction_R2": float(result["median_R2"].median()),
        "median_unique_direction_RMSE": float(result["median_RMSE"].median()),
    }
    return result, summary


def make_report(
    seed_summary: pd.DataFrame,
    consistency: pd.DataFrame,
    modal_success: dict[str, Any],
    exceptional: pd.DataFrame,
) -> str:
    lines = [
        "AIEF intertwining and controller-equilibrium analysis",
        "====================================================",
        "",
        "Intertwining",
        "------------",
        f"Seeds: {len(seed_summary)}",
        f"Median CD=LC residual: {seed_summary['intertwining_residual_relative'].median():.6g}",
        f"Maximum CD=LC residual: {seed_summary['intertwining_residual_relative'].max():.6g}",
        f"Median tangent commutator: {seed_summary['tangent_commutator_relative'].median():.6g}",
        f"Multiplicity matches: {int(seed_summary['all_channel_multiplicities_match'].sum())}/{len(seed_summary)}",
        "",
        "Controller equilibrium",
        "----------------------",
        f"Median controller residual: {seed_summary['controller_equilibrium_residual_relative'].median():.6g}",
        f"Maximum controller residual: {seed_summary['controller_equilibrium_residual_relative'].max():.6g}",
        f"Median edge-balance residual: {seed_summary['edge_balance_residual_relative'].median():.6g}",
        "",
        "Repeated fingerprint consistency",
        "--------------------------------",
    ]
    for _, row in consistency.loc[consistency["seed_count"] >= 2].iterrows():
        lines.append(
            f"  {row['signature_type']} {row['signature']}: "
            f"seeds={int(row['seed_count'])}, "
            f"max_spectrum_error={row['maximum_matched_spectrum_error']:.6g}, "
            f"same={row['same_spectrum_within_tolerance']}, "
            f"max_CDLC={row['intertwining_residual_max']:.3g}"
        )

    lines.extend(["", "Unique-direction modal prediction", "---------------------------------"])
    for key, value in modal_success.items():
        lines.append(f"  {key}: {value}")

    lines.extend(["", "Exceptional switching layer", "---------------------------"])
    for _, row in exceptional.iterrows():
        lines.append(
            f"  {row['stage']}: face={row['face_hash']}, "
            f"dim={int(row['tangent_dimension'])}, "
            f"channels={row['channel_count']}, "
            f"CDLC={row['intertwining_residual_relative']:.3g}, "
            f"commutator={row['tangent_commutator_relative']:.3g}, "
            f"controller_residual={row['controller_equilibrium_residual_relative']:.3g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* CD=LC is tested numerically using a least-squares node-space intertwiner.",
            "* Geometry signatures are descriptive, not complete isomorphism invariants.",
            "* Mature channel values may be discrete empirically without forming a universal finite alphabet.",
            "* Exceptional post-switch states can temporarily violate exact channel invariance.",
            "* Modal success is counted by unique seed/direction, not repeated amplitude rows.",
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
    parser.add_argument("--modal-summary", default=DEFAULT_MODAL_SUMMARY)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--exceptional-seed", default=DEFAULT_EXCEPTIONAL_SEED)
    parser.add_argument(
        "--exceptional-check-times",
        type=base.parse_float_list,
        default=base.parse_float_list(DEFAULT_EXCEPTIONAL_CHECK_TIMES),
    )
    parser.add_argument(
        "--spectrum-tol", type=float, default=DEFAULT_SPECTRUM_TOL
    )
    parser.add_argument(
        "--channel-tol", type=float, default=DEFAULT_CHANNEL_TOL
    )
    parser.add_argument(
        "--subspace-tol", type=float, default=DEFAULT_SUBSPACE_TOL
    )
    parser.add_argument("--modal-r2", type=float, default=DEFAULT_MODAL_R2)
    parser.add_argument(
        "--min-amplitude-fraction",
        type=float,
        default=0.9,
    )
    parser.add_argument(
        "--min-relative-amplitude",
        type=float,
        default=1e-6,
    )
    parser.add_argument("--typical-rate", type=float, default=0.3157894736842105)
    parser.add_argument("--slow-cutoff", type=float, default=0.25)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (
        args.scalar,
        args.npz,
        args.manifest,
        args.tangent_results,
        args.modal_summary,
    ):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(args.spectrum_tol, args.channel_tol, args.subspace_tol) <= 0.0:
        raise ValueError("tolerances must be positive")
    os.makedirs(args.output_dir, exist_ok=True)

    scalar = pd.read_csv(args.scalar, dtype={"seed": str})
    scalar["seed"] = scalar["seed"].astype(str)
    tangent = pd.read_csv(args.tangent_results, dtype={"seed": str})
    modal = pd.read_csv(args.modal_summary, dtype={"seed": str})
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    direction_summary, _, _ = tangent_analysis.tangent_direction_summary(
        tangent,
        args.min_amplitude_fraction,
        args.min_relative_amplitude,
        args.typical_rate,
        args.slow_cutoff,
    )

    model = manifest["model"]
    node_count = int(model["N"])
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(node_count, capacity)
    A, edges = base.incidence_matrix(node_count)
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].astype(str), key=int
    )

    seed_rows: list[dict[str, Any]] = []
    channel_rows: list[dict[str, Any]] = []
    node_rows: list[dict[str, Any]] = []
    exceptional_rows: list[dict[str, Any]] = []
    matrix_payload: dict[str, np.ndarray] = {}

    with np.load(args.npz, allow_pickle=False) as data:
        for seed in seeds:
            state = base.load_split_state(data, seed)
            summary, channels, nodes, matrices = channel_and_intertwining(
                state,
                model,
                capacities,
                A,
                edges,
                boundary_tolerance=1e-9,
                channel_tolerance=args.channel_tol,
                subspace_tolerance=args.subspace_tol,
            )
            J = matrices["J_tangent"]
            for node in nodes:
                node_rows.append({"seed": seed, **node})
            for matrix_name, matrix in matrices.items():
                matrix_payload[f"seed_{seed}_{matrix_name}"] = matrix
            components = face.face_components(
                state, model, capacities, A, edges, 1e-9
            )
            seed_rows.append(
                {
                    "seed": seed,
                    **summary,
                    "spectrum_values_json": json.dumps(
                        spectrum_vector(J).tolist(), separators=(",", ":")
                    ),
                }
            )
            for channel in channels:
                channel_rows.append({"seed": seed, **channel})

        stages, transition = face.exceptional_states(
            data,
            args.exceptional_seed,
            manifest,
            capacities,
            A,
            edges,
            1e-9,
            args.exceptional_check_times,
        )
        for stage, state in stages.items():
            summary, channels, nodes, matrices = channel_and_intertwining(
                state,
                model,
                capacities,
                A,
                edges,
                boundary_tolerance=1e-9,
                channel_tolerance=args.channel_tol,
                subspace_tolerance=args.subspace_tol,
            )
            J = matrices["J_tangent"]
            for matrix_name, matrix in matrices.items():
                matrix_payload[f"exceptional_{stage}_{matrix_name}"] = matrix
            exceptional_rows.append(
                {
                    "stage": stage,
                    **summary,
                    "spectrum_values_json": json.dumps(
                        spectrum_vector(J).tolist(), separators=(",", ":")
                    ),
                    "field_norm": float(
                        np.linalg.norm(
                            face.face_components(
                                state,
                                model,
                                capacities,
                                A,
                                edges,
                                1e-9,
                            )["field"]
                        )
                    ),
                }
            )

    channel_summary = pd.DataFrame(seed_rows)
    channel_details = pd.DataFrame(channel_rows)
    node_details = pd.DataFrame(node_rows)
    exceptional = pd.DataFrame(exceptional_rows)
    consistency = tolerance_spectrum_consistency(
        channel_summary, args.spectrum_tol
    )
    modal_by_direction, modal_success = unique_direction_modal_success(
        modal,
        direction_summary,
        args.modal_r2,
    )

    outputs = {
        "channel_invariance_by_seed.csv": channel_summary,
        "channel_multiplicities_by_seed.csv": channel_details,
        "node_controller_equilibrium_by_seed.csv": node_details,
        "geometry_spectrum_consistency_tolerant.csv": consistency,
        "unique_direction_modal_success.csv": modal_by_direction,
        "exceptional_channel_stages.csv": exceptional,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(args.output_dir, filename), index=False)
    np.savez_compressed(
        os.path.join(args.output_dir, "intertwining_controller_matrices.npz"),
        **matrix_payload,
    )

    with open(
        os.path.join(args.output_dir, "modal_success_summary.json"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(modal_success, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(
        os.path.join(args.output_dir, "exceptional_transition_metadata.json"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(transition, handle, indent=2, sort_keys=True)
        handle.write("\n")

    report = make_report(
        channel_summary,
        consistency,
        modal_success,
        exceptional,
    )
    with open(
        os.path.join(args.output_dir, "channel_invariance_report.txt"),
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(report)
    print(report)

    analysis_manifest = {
        "analysis": "AIEF tangent-channel invariance and tolerance-aware spectra",
        "scalar_path": str(Path(args.scalar).resolve()),
        "scalar_sha256": file_sha256(args.scalar),
        "npz_path": str(Path(args.npz).resolve()),
        "npz_sha256": file_sha256(args.npz),
        "source_manifest_path": str(Path(args.manifest).resolve()),
        "source_manifest_sha256": file_sha256(args.manifest),
        "tangent_results_path": str(Path(args.tangent_results).resolve()),
        "tangent_results_sha256": file_sha256(args.tangent_results),
        "modal_summary_path": str(Path(args.modal_summary).resolve()),
        "modal_summary_sha256": file_sha256(args.modal_summary),
        "spectrum_tolerance": args.spectrum_tol,
        "channel_tolerance": args.channel_tol,
        "subspace_tolerance": args.subspace_tol,
        "modal_R2_threshold": args.modal_r2,
        "exceptional_seed": args.exceptional_seed,
        "exceptional_check_times": args.exceptional_check_times,
        "notes": [
            "Geometry signatures are not complete graph-isomorphism canonical forms.",
            "Spectrum equality is tolerance-based, not bitwise.",
            "Channel multiplicity inference assumes tangent/channel invariance.",
            "Unique seed/direction is the independent directional unit for modal success.",
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
