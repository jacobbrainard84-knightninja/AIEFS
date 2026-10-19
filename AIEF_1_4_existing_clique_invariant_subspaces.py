#!/usr/bin/env python3
"""Test geometric/dual invariant subspaces on existing AIEF K4/K5/K6 cliques.

This analysis uses only the frozen AIEF-1.4 split states.  For every complete,
fully saturated positive-support K4, K5, or K6 component it constructs the
signless-incidence face-lineality basis V=ker(C), takes the orthonormal dual
U=V, and tests

    K V = V Lambda,
    U^T K = Lambda U^T,
    U^T V = I.

Here K is the exact frozen-driver finite-step tangent action on row-sum-fiber
directions.  Since A h=0, node scales remain fixed exactly and the post-
positivity admissibility map is diagonal on the fiber.  The script checks
subspace invariance, scalar-on-subspace action, finite-step/continuous rates,
and centered nonlinear one-step perturbations with the replayed R driver.

Components within one seed are descriptive and are not treated as independent
experimental replicates.  The seed/graph remains the inferential unit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import AIEF_1_4_stationarity_perturbation_analysis_updated as base
import AIEF_1_4_face_spectrum_analysis as face
import AIEF_1_4_component_controller_audit as component_audit
import AIEF_1_4_actual_admissibility_branch_audit as branch_audit
import AIEF_1_4_frozen_driver_cocycle_analysis as frozen


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_SCALAR = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_scalar_summary.csv"
)
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_existing_clique_invariant_subspaces"
DEFAULT_BOUNDARY_TOL = 1e-9
DEFAULT_SUPPORT_TOL = 1e-14
DEFAULT_RANK_TOL = 1e-10
DEFAULT_AMPLITUDE_FRACTIONS = "1e-6,1e-5,1e-4"
ZERO_TOL = 1e-14


def file_sha256(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_positive_float_list(value: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated floats") from exc
    if not values or any(value <= 0.0 for value in values):
        raise argparse.ArgumentTypeError("values must be positive")
    return sorted(set(values))


def json_compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def nullspace_basis(matrix: np.ndarray, rank_tolerance: float) -> tuple[np.ndarray, int]:
    matrix = np.asarray(matrix, dtype=float)
    if matrix.size == 0:
        return np.eye(matrix.shape[1]), 0
    _, singular, vh = np.linalg.svd(matrix, full_matrices=True)
    rank = int(np.sum(singular > rank_tolerance))
    return vh[rank:].T, rank


def complete_graph_label(node_count: int) -> str:
    return f"K{node_count}"


def make_report(
    components: pd.DataFrame,
    directions: pd.DataFrame,
) -> str:
    lines = [
        "AIEF existing-clique invariant-subspace analysis",
        "================================================",
        "",
        "Component counts",
        "----------------",
    ]
    for clique_size, group in components.groupby("clique_size"):
        lines.append(
            f"  K{int(clique_size)}: components={len(group)}, "
            f"seeds={group['seed'].nunique()}, tangent_dim={int(group['tangent_dimension'].iloc[0])}"
        )

    lines.extend(["", "Invariant-subspace diagnostics", "------------------------------"])
    for clique_size, group in components.groupby("clique_size"):
        lines.append(
            f"  K{int(clique_size)}: max_CV={group['constraint_basis_residual'].max():.3g}, "
            f"max_UtV={group['duality_residual'].max():.3g}, "
            f"max_right={group['right_invariance_relative'].max():.3g}, "
            f"max_left={group['left_invariance_relative'].max():.3g}, "
            f"max_scalarity={group['reduced_scalarity_relative'].max():.3g}, "
            f"max_scale_spread={group['edge_scale_spread'].max():.3g}, "
            f"median_step_rate={group['finite_step_rate'].median():.9g}, "
            f"expected_continuous_rate={group['expected_continuous_rate'].median():.9g}"
        )

    lines.extend(["", "Centered nonlinear one-step checks", "----------------------------------"])
    for clique_size, group in directions.groupby("clique_size"):
        lines.append(
            f"  K{int(clique_size)}: rows={len(group)}, "
            f"all_fiber_formulas_preserved={bool(group['fiber_formula_preserved'].all())}, "
            f"winner_signature_preserved_fraction={group['winner_signature_preserved'].mean():.3g}, "
            f"median_error={group['relative_error'].median():.3g}, "
            f"maximum_error={group['relative_error'].max():.3g}, "
            f"maximum_row_sum_drift={group['proposal_row_sum_tangent_residual'].max():.3g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Components are repeated within seeds and are not independent replicates.",
            "* U=V is justified here because V is orthonormal and the exact fiber action is diagonal/symmetric.",
            "* Scalar-on-subspace action is component-specific; it does not imply rank-one full dynamics.",
            "* Finite-step rates are distinct from continuous ideal rates by O(dt) and safeguard effects.",
            "* Results use existing split states only; no new cohort was generated.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scalar", default=DEFAULT_SCALAR)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--boundary-tol", type=float, default=DEFAULT_BOUNDARY_TOL)
    parser.add_argument("--support-tol", type=float, default=DEFAULT_SUPPORT_TOL)
    parser.add_argument("--rank-tol", type=float, default=DEFAULT_RANK_TOL)
    parser.add_argument(
        "--amplitude-fractions",
        type=parse_positive_float_list,
        default=parse_positive_float_list(DEFAULT_AMPLITUDE_FRACTIONS),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.scalar, args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(args.boundary_tol, args.support_tol, args.rank_tol) <= 0.0:
        raise ValueError("tolerances must be positive")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    scalar = pd.read_csv(args.scalar, dtype={"seed": str})
    scalar["seed"] = scalar["seed"].astype(str)
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    model = manifest["model"]
    node_count = int(model["N"])
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(node_count, capacity)
    A, edges = base.incidence_matrix(node_count)
    dt = float(model["dt"])
    gamma = float(model["gamma"])
    eta = float(model["eta"])
    seeds = sorted(
        scalar.loc[scalar["branch"] == "continue", "seed"].unique(),
        key=int,
    )

    component_rows: list[dict[str, Any]] = []
    direction_rows: list[dict[str, Any]] = []
    matrix_payload: dict[str, np.ndarray] = {}

    with np.load(args.npz, allow_pickle=False) as data:
        for seed in seeds:
            state = base.load_split_state(data, seed)
            face_components = face.face_components(
                state,
                model,
                capacities,
                A,
                edges,
                args.boundary_tol,
            )
            support = np.asarray(face_components["w"]) > args.support_tol
            support_indices = np.flatnonzero(support)
            graph_components = component_audit.connected_support_components(
                node_count, support_indices, edges
            )
            branch = branch_audit.proposal_and_admissibility_branch(
                state,
                model,
                capacities,
                A,
                edges,
                1e-12,
            )
            R_base = branch["R_matrix"]

            for component_index, graph_component in enumerate(graph_components):
                nodes = graph_component["nodes"]
                component_edges = graph_component["edges"]
                size = len(nodes)
                if size not in {4, 5, 6}:
                    continue
                if len(component_edges) != size * (size - 1) // 2:
                    continue
                saturated = np.asarray(face_components["saturated"], dtype=bool)
                if not np.all(saturated[nodes]):
                    continue

                C = A[np.ix_(nodes, component_edges)]
                V, rank = nullspace_basis(C, args.rank_tol)
                tangent_dimension = V.shape[1]
                expected_dimension = size * (size - 3) // 2
                if tangent_dimension != expected_dimension:
                    raise RuntimeError(
                        f"{seed} K{size}: nullity {tangent_dimension} != {expected_dimension}"
                    )
                U = V.copy()
                edge_scales = branch["edge_scales"][component_edges]
                step_diagonal = (1.0 - gamma * dt) * edge_scales
                K_local = np.diag(step_diagonal)
                reduced = U.T @ K_local @ V
                mean_multiplier = float(np.trace(reduced) / tangent_dimension)
                projector = V @ V.T
                right_error = K_local @ V - V @ reduced
                left_error = U.T @ K_local - reduced @ U.T
                right_relative = float(
                    np.linalg.norm(right_error)
                    / max(np.linalg.norm(K_local @ V), ZERO_TOL)
                )
                left_relative = float(
                    np.linalg.norm(left_error)
                    / max(np.linalg.norm(U.T @ K_local), ZERO_TOL)
                )
                scalarity = float(
                    np.linalg.norm(
                        reduced - mean_multiplier * np.eye(tangent_dimension)
                    )
                    / max(np.linalg.norm(reduced), ZERO_TOL)
                )
                finite_rate = float(-math.log(abs(mean_multiplier)) / dt)
                expected_rate = float((size - 1) * eta / capacity)
                key = f"seed_{seed}_component_{component_index}_K{size}"
                matrix_payload[f"{key}_C"] = C
                matrix_payload[f"{key}_V"] = V
                matrix_payload[f"{key}_U"] = U
                matrix_payload[f"{key}_K"] = K_local
                matrix_payload[f"{key}_Lambda"] = reduced

                component_rows.append(
                    {
                        "seed": seed,
                        "component_index": component_index,
                        "clique": complete_graph_label(size),
                        "clique_size": size,
                        "nodes": ";".join(map(str, nodes.tolist())),
                        "edges": ";".join(map(str, component_edges.tolist())),
                        "edge_count": len(component_edges),
                        "incidence_rank": rank,
                        "tangent_dimension": tangent_dimension,
                        "expected_tangent_dimension": expected_dimension,
                        "constraint_basis_residual": float(np.linalg.norm(C @ V)),
                        "duality_residual": float(
                            np.linalg.norm(U.T @ V - np.eye(tangent_dimension))
                        ),
                        "right_invariance_relative": right_relative,
                        "left_invariance_relative": left_relative,
                        "reduced_scalarity_relative": scalarity,
                        "edge_scale_mean": float(np.mean(edge_scales)),
                        "edge_scale_spread": float(np.ptp(edge_scales)),
                        "mean_step_multiplier": mean_multiplier,
                        "finite_step_rate": finite_rate,
                        "expected_continuous_rate": expected_rate,
                        "finite_minus_continuous_rate": finite_rate - expected_rate,
                        "support_min_proposal": float(
                            np.min(branch["x"][component_edges])
                        ),
                        "minimum_branch_margin": float(
                            np.min(branch["winner_margin"][component_edges])
                        ),
                    }
                )

                # Centered exact-fiber checks and frozen nonlinear one-step checks.
                for direction_id in range(tangent_dimension):
                    local_direction = V[:, direction_id]
                    full_direction = np.zeros(len(edges[0]))
                    full_direction[component_edges] = local_direction
                    direction_matrix = base.vector_to_matrix(
                        full_direction, node_count, edges
                    )
                    maximum = frozen.maximum_symmetric_feasible_amplitude(
                        state.B[edges], full_direction, A, capacities
                    )
                    edge_limit = float(
                        np.min(
                            branch["x"][component_edges]
                            / np.maximum(np.abs(local_direction), 1e-15)
                        )
                    )
                    for fraction in args.amplitude_fractions:
                        amplitude = min(
                            fraction * edge_limit,
                            0.25 * maximum if np.isfinite(maximum) else fraction * edge_limit,
                        )
                        if not np.isfinite(amplitude) or amplitude <= 1e-14:
                            continue

                        # Pure post-positivity fiber map.
                        x_plus = branch["x"] + amplitude * full_direction
                        x_minus = branch["x"] - amplitude * full_direction
                        y_plus, plus_info = branch_audit.admissibility_from_nonnegative_proposal(
                            x_plus, capacities, A, edges, 1e-12
                        )
                        y_minus, minus_info = branch_audit.admissibility_from_nonnegative_proposal(
                            x_minus, capacities, A, edges, 1e-12
                        )
                        pure_centered = (
                            y_plus[component_edges] - y_minus[component_edges]
                        ) / (2.0 * amplitude)
                        pure_expected = edge_scales * local_direction
                        pure_error = float(
                            np.linalg.norm(pure_centered - pure_expected)
                            / max(np.linalg.norm(pure_expected), ZERO_TOL)
                        )

                        # Full frozen-driver one-step map from B perturbations.
                        B_plus = state.B + amplitude * direction_matrix
                        B_minus = state.B - amplitude * direction_matrix
                        plus_branch = frozen.frozen_weight_branch(
                            B_plus,
                            R_base,
                            model,
                            capacities,
                            A,
                            edges,
                            1e-12,
                        )
                        minus_branch = frozen.frozen_weight_branch(
                            B_minus,
                            R_base,
                            model,
                            capacities,
                            A,
                            edges,
                            1e-12,
                        )
                        nonlinear_centered = (
                            plus_branch["projected"][edges][component_edges]
                            - minus_branch["projected"][edges][component_edges]
                        ) / (2.0 * amplitude)
                        expected = K_local @ local_direction
                        relative_error = float(
                            np.linalg.norm(nonlinear_centered - expected)
                            / max(np.linalg.norm(expected), ZERO_TOL)
                        )
                        base_signature = frozen.branch_signature(branch, component_edges)
                        plus_signature = frozen.branch_signature(plus_branch, component_edges)
                        minus_signature = frozen.branch_signature(minus_branch, component_edges)
                        winner_signature_preserved = bool(
                            plus_signature == base_signature
                            and minus_signature == base_signature
                        )
                        endpoint_nodes = np.unique(
                            np.concatenate(
                                [edges[0][component_edges], edges[1][component_edges]]
                            )
                        )
                        fiber_formula_preserved = bool(
                            plus_branch["gate_on"] == branch["gate_on"]
                            and minus_branch["gate_on"] == branch["gate_on"]
                            and np.array_equal(
                                plus_branch["clipped"][endpoint_nodes],
                                branch["clipped"][endpoint_nodes],
                            )
                            and np.array_equal(
                                minus_branch["clipped"][endpoint_nodes],
                                branch["clipped"][endpoint_nodes],
                            )
                            and np.allclose(
                                plus_branch["edge_scales"][component_edges],
                                branch["edge_scales"][component_edges],
                                rtol=0.0,
                                atol=1e-12,
                            )
                            and np.allclose(
                                minus_branch["edge_scales"][component_edges],
                                branch["edge_scales"][component_edges],
                                rtol=0.0,
                                atol=1e-12,
                            )
                        )
                        proposal_row_tangent = A[:, component_edges] @ local_direction

                        direction_rows.append(
                            {
                                "seed": seed,
                                "component_index": component_index,
                                "clique": complete_graph_label(size),
                                "clique_size": size,
                                "direction_id": direction_id,
                                "amplitude_fraction": fraction,
                                "amplitude": amplitude,
                                "pure_fiber_relative_error": pure_error,
                                "relative_error": relative_error,
                                "fiber_formula_preserved": fiber_formula_preserved,
                                "winner_signature_preserved": winner_signature_preserved,
                                "proposal_row_sum_tangent_residual": float(
                                    np.linalg.norm(proposal_row_tangent)
                                ),
                                "plus_gate": bool(plus_info["gate_on"]),
                                "minus_gate": bool(minus_info["gate_on"]),
                            }
                        )

    component_frame = pd.DataFrame(component_rows)
    direction_frame = pd.DataFrame(direction_rows)
    if not len(component_frame):
        raise RuntimeError("no fully saturated K4/K5/K6 components found")

    component_audit.atomic_write_csv(
        output_dir / "clique_invariant_subspace_by_component.csv",
        component_frame,
    )
    component_audit.atomic_write_csv(
        output_dir / "clique_fiber_direction_checks.csv",
        direction_frame,
    )
    component_audit.atomic_savez(
        output_dir / "clique_invariant_subspace_matrices.npz",
        matrix_payload,
    )

    report = make_report(component_frame, direction_frame)
    component_audit.atomic_write_text(
        output_dir / "clique_invariant_subspace_report.txt",
        report,
    )

    source_path = Path(__file__).resolve()
    dependencies = {
        "stationarity": Path(base.__file__).resolve(),
        "face_spectrum": Path(face.__file__).resolve(),
        "component_audit": Path(component_audit.__file__).resolve(),
        "branch_audit": Path(branch_audit.__file__).resolve(),
        "frozen_cocycle": Path(frozen.__file__).resolve(),
    }
    analysis_manifest = {
        "analysis": "AIEF-1.4 existing clique biorthogonal invariant subspaces",
        "source": {
            "path": str(source_path),
            "sha256": file_sha256(source_path),
        },
        "dependencies": {
            name: {"path": str(path), "sha256": file_sha256(path)}
            for name, path in dependencies.items()
        },
        "command": sys.argv,
        "inputs": {
            "scalar": {
                "path": str(Path(args.scalar).resolve()),
                "sha256": file_sha256(args.scalar),
            },
            "npz": {
                "path": str(Path(args.npz).resolve()),
                "sha256": file_sha256(args.npz),
            },
            "manifest": {
                "path": str(Path(args.manifest).resolve()),
                "sha256": file_sha256(args.manifest),
            },
        },
        "production_run_hash": DEFAULT_RUN_HASH,
        "seed_count": len(seeds),
        "component_count": len(component_frame),
        "component_counts": {
            f"K{int(size)}": int(len(group))
            for size, group in component_frame.groupby("clique_size")
        },
        "boundary_tolerance": args.boundary_tol,
        "support_tolerance": args.support_tol,
        "rank_tolerance": args.rank_tol,
        "amplitude_fractions": args.amplitude_fractions,
        "outputs": [
            "clique_invariant_subspace_by_component.csv",
            "clique_fiber_direction_checks.csv",
            "clique_invariant_subspace_matrices.npz",
            "clique_invariant_subspace_report.txt",
        ],
        "interpretation_constraints": [
            "Components within a seed are not independent experimental units.",
            "The tested finite-step tangent is the frozen-driver row-sum-fiber action.",
            "Higher cliques have multidimensional lineality; this is not a rank-one claim.",
            "No new simulations or seed cohorts were generated.",
        ],
    }
    component_audit.atomic_write_text(
        output_dir / "analysis_manifest.json",
        json.dumps(analysis_manifest, indent=2, sort_keys=True) + "\n",
    )

    print(report)
    print(f"Saved analysis to {output_dir.resolve()}")


if __name__ == "__main__":
    main()
