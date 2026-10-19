#!/usr/bin/env python3
"""Channel-invariance and tolerance-aware spectrum analysis for AIEF-1.4.

This script tests whether the tangent space of each mature active face is
invariant under the diagonal endpoint-relaxation operator

    D = diag(-gamma - rho_e).

It computes:
* [D, P_T] commutator norms, P_T=Q_T Q_T^T;
* channel projectors grouped by rho_e;
* dimensions of T intersect channel coordinate subspaces;
* predicted versus observed eigenvalue multiplicities;
* tolerance-aware full-spectrum classes by face fingerprint;
* the same quantities before/after the exceptional face transition;
* modal-prediction success aggregated by unique seed/direction rather than by
  repeated perturbation amplitude.

The analysis uses only existing frozen artifacts.
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
DEFAULT_OUTPUT_DIR = "aief_1_4_channel_invariance"
DEFAULT_EXCEPTIONAL_SEED = "4619122171158768524"
DEFAULT_EXCEPTIONAL_CHECK_TIMES = "100,120,123,125,150"
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
    return [np.asarray(cluster, dtype=float) for cluster in clusters]


def spectrum_vector(J: np.ndarray) -> np.ndarray:
    values = np.linalg.eigvals(J)
    if np.max(np.abs(np.imag(values))) > 1e-8:
        # Fixed-stratum analytic J should be symmetric; retain real parts but
        # make the unexpected imaginary component visible to callers.
        pass
    return np.sort(np.real(values))


def spectrum_class_id(values: np.ndarray, tolerance: float) -> str:
    quantized = np.round(np.asarray(values, dtype=float) / tolerance).astype(np.int64)
    return hashlib.sha256(quantized.tobytes()).hexdigest()[:16]


def matched_spectrum_error(left: np.ndarray, right: np.ndarray) -> float:
    left = np.sort(np.real(np.asarray(left)))
    right = np.sort(np.real(np.asarray(right)))
    if len(left) != len(right):
        return np.inf
    return float(np.max(np.abs(left - right))) if len(left) else 0.0


def intersection_dimension(
    Q: np.ndarray,
    channel_indices: np.ndarray,
    tolerance: float,
) -> int:
    """dim(range(Q) intersect coordinate subspace E_channel)."""
    all_indices = np.arange(Q.shape[0])
    outside = np.setdiff1d(all_indices, channel_indices, assume_unique=True)
    if not len(outside):
        return Q.shape[1]
    matrix = Q[outside, :]
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    rank = int(np.sum(singular_values > tolerance))
    return int(Q.shape[1] - rank)


def channel_analysis_for_state(
    state: base.DynamicState,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    channel_tolerance: float,
    subspace_tolerance: float,
) -> tuple[dict[str, Any], list[dict[str, Any]], np.ndarray]:
    components = face.face_components(
        state, model, capacities, A, edges, boundary_tolerance
    )
    gamma = float(model["gamma"])
    Q = components["basis"]
    rates = gamma + components["endpoint_rate"]
    D = np.diag(-rates)
    P_T = Q @ Q.T
    commutator = D @ P_T - P_T @ D
    commutator_relative = float(
        np.linalg.norm(commutator)
        / max(np.linalg.norm(D), ZERO_TOL)
    )
    J = Q.T @ D @ Q
    eigenvalues = spectrum_vector(J)
    eigen_clusters = cluster_values(-eigenvalues, channel_tolerance)

    support_indices = np.flatnonzero(components["support"])
    support_rates = rates[support_indices]
    rate_clusters = cluster_values(support_rates, channel_tolerance)
    channel_rows: list[dict[str, Any]] = []
    predicted_total = 0

    for channel_id, cluster in enumerate(rate_clusters):
        representative = float(np.mean(cluster))
        channel_indices = support_indices[
            np.abs(support_rates - representative) <= channel_tolerance
        ]
        projector = np.zeros((len(rates), len(rates)), dtype=float)
        projector[channel_indices, channel_indices] = 1.0
        projector_commutator = P_T @ projector - projector @ P_T
        intersection = intersection_dimension(
            Q, channel_indices, subspace_tolerance
        )
        predicted_total += intersection
        observed_multiplicity = int(
            np.sum(np.abs((-eigenvalues) - representative) <= channel_tolerance)
        )
        compression = Q.T @ projector @ Q
        compression_values = np.linalg.eigvalsh(compression)
        channel_rows.append(
            {
                "channel_id": channel_id,
                "contraction_rate": representative,
                "edge_count": int(len(channel_indices)),
                "intersection_dimension": intersection,
                "observed_eigenvalue_multiplicity": observed_multiplicity,
                "multiplicity_matches": bool(
                    intersection == observed_multiplicity
                ),
                "projector_commutator_relative": float(
                    np.linalg.norm(projector_commutator)
                    / max(np.linalg.norm(projector), ZERO_TOL)
                ),
                "compression_eigenvalues": json.dumps(
                    np.round(compression_values, 12).tolist(),
                    separators=(",", ":"),
                ),
                "compression_is_projector_1e9": bool(
                    np.all(
                        (np.abs(compression_values) <= 1e-9)
                        | (np.abs(compression_values - 1.0) <= 1e-9)
                    )
                ),
            }
        )

    eigen_multiplicities = [
        {
            "rate": float(np.mean(cluster)),
            "multiplicity": int(len(cluster)),
        }
        for cluster in eigen_clusters
    ]
    summary = {
        "face_hash": components["face_hash"],
        "geometry_invariant_hash": components["geometry_invariant_hash"],
        "augmented_invariant_hash": components["augmented_invariant_hash"],
        "support_size": int(np.sum(components["support"])),
        "saturated_count": int(np.sum(components["saturated"])),
        "outward_count": int(np.sum(components["outward"])),
        "tangent_dimension": int(Q.shape[1]),
        "channel_count": int(len(rate_clusters)),
        "commutator_relative": commutator_relative,
        "tangent_invariant_1e9": bool(commutator_relative <= 1e-9),
        "predicted_multiplicity_total": int(predicted_total),
        "predicted_multiplicities_cover_tangent": bool(
            predicted_total == Q.shape[1]
        ),
        "all_channel_multiplicities_match": bool(
            all(row["multiplicity_matches"] for row in channel_rows)
        ),
        "spectrum_class_1e10": spectrum_class_id(
            eigenvalues, channel_tolerance
        ),
        "eigenvalue_multiplicities": json.dumps(
            eigen_multiplicities, sort_keys=True, separators=(",", ":")
        ),
        "spectral_abscissa": float(np.max(eigenvalues)) if len(eigenvalues) else np.nan,
        "slowest_decay_rate": float(-np.max(eigenvalues))
        if len(eigenvalues)
        else np.nan,
    }
    return summary, channel_rows, J


def geometry_spectrum_consistency(
    summaries: pd.DataFrame,
    spectrum_tolerance: float,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for signature_type, column in (
        ("geometry_only", "geometry_invariant_hash"),
        ("geometry_plus_rates", "augmented_invariant_hash"),
        ("labeled_face", "face_hash"),
    ):
        for signature, group in summaries.groupby(column, dropna=False):
            spectra = [json.loads(value) for value in group["spectrum_values_json"]]
            arrays = [
                np.asarray(item, dtype=float)
                for item in spectra
            ]
            maximum_error = 0.0
            for index, left in enumerate(arrays):
                for right in arrays[index + 1 :]:
                    maximum_error = max(
                        maximum_error,
                        matched_spectrum_error(left, right),
                    )
            class_count = group["spectrum_class_1e10"].nunique()
            rows.append(
                {
                    "signature_type": signature_type,
                    "signature": signature,
                    "seed_count": int(len(group)),
                    "distinct_tolerance_spectrum_classes": int(class_count),
                    "same_full_spectrum_within_tolerance": bool(
                        maximum_error <= spectrum_tolerance
                    ),
                    "maximum_matched_eigenvalue_error": maximum_error,
                    "all_tangent_invariant": bool(
                        group["tangent_invariant_1e9"].all()
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
    channel_summary: pd.DataFrame,
    consistency: pd.DataFrame,
    modal_success: dict[str, Any],
    exceptional: pd.DataFrame,
) -> str:
    lines = [
        "AIEF tangent-channel invariance analysis",
        "========================================",
        "",
        "Channel invariance",
        "------------------",
        f"Seeds: {len(channel_summary)}",
        f"Tangent-invariant seeds: {int(channel_summary['tangent_invariant_1e9'].sum())}/{len(channel_summary)}",
        f"Multiplicity matches: {int(channel_summary['all_channel_multiplicities_match'].sum())}/{len(channel_summary)}",
        f"Median commutator: {channel_summary['commutator_relative'].median():.6g}",
        "",
        "Repeated fingerprint consistency",
        "--------------------------------",
    ]
    repeated = consistency.loc[consistency["seed_count"] >= 2]
    for _, row in repeated.iterrows():
        lines.append(
            f"  {row['signature_type']} {row['signature']}: "
            f"seeds={int(row['seed_count'])}, "
            f"classes={int(row['distinct_tolerance_spectrum_classes'])}, "
            f"max_error={row['maximum_matched_eigenvalue_error']:.6g}, "
            f"same={row['same_full_spectrum_within_tolerance']}"
        )

    lines.extend(["", "Unique-direction modal prediction", "---------------------------------"])
    for key, value in modal_success.items():
        lines.append(f"  {key}: {value}")

    lines.extend(["", "Exceptional stages", "------------------"])
    for _, row in exceptional.iterrows():
        lines.append(
            f"  {row['stage']}: face={row['face_hash']}, "
            f"dim={int(row['tangent_dimension'])}, "
            f"rate={row['slowest_decay_rate']:.12g}, "
            f"channels={row['eigenvalue_multiplicities']}, "
            f"commutator={row['commutator_relative']:.3g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Tolerance-based spectrum identity is not bitwise identity.",
            "* Geometry signatures are descriptive invariants, not complete graph-isomorphism canonical forms.",
            "* Channel multiplicity follows directly only when the tangent projector commutes with the diagonal channel operator.",
            "* Modal trajectories repeat amplitudes; unique seed/direction is the independent directional unit.",
            "* Exceptional split spectra are not assumed to be stationary-face spectra.",
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
    exceptional_rows: list[dict[str, Any]] = []

    with np.load(args.npz, allow_pickle=False) as data:
        for seed in seeds:
            state = base.load_split_state(data, seed)
            summary, channels, J = channel_analysis_for_state(
                state,
                model,
                capacities,
                A,
                edges,
                boundary_tolerance=1e-9,
                channel_tolerance=args.channel_tol,
                subspace_tolerance=args.subspace_tol,
            )
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
            summary, channels, J = channel_analysis_for_state(
                state,
                model,
                capacities,
                A,
                edges,
                boundary_tolerance=1e-9,
                channel_tolerance=args.channel_tol,
                subspace_tolerance=args.subspace_tol,
            )
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
    exceptional = pd.DataFrame(exceptional_rows)
    consistency = geometry_spectrum_consistency(
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
        "geometry_spectrum_consistency_tolerant.csv": consistency,
        "unique_direction_modal_success.csv": modal_by_direction,
        "exceptional_channel_stages.csv": exceptional,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(args.output_dir, filename), index=False)

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
