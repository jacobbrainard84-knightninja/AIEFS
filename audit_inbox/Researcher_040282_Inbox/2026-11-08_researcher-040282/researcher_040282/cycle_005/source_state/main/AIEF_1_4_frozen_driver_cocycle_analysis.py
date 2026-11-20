#!/usr/bin/env python3
"""Frozen-driver finite-time cocycle analysis for the exceptional AIEF K3.

This is Stage A of the variational program.  It treats the replayed coherence
sequence R_n as exogenous and studies only the weight-sector update

    w_{n+1} = A_eps([w_n + dt F_n]_+),
    F_n = (eta + mu) R_n - mu - gamma w_n.

On the positive K3 proposal branch, the frozen-driver variational matrix is

    K_n^(B) = (1 - gamma dt) D A_eps(x_n).

The script constructs the exact 3x3 K3 matrix sequence, finite-horizon
propagators, singular values, finite-time exponents, QR rates, non-normality,
adjacent commutators, and sampled sliding-window amplification.  It also
compares the cocycle against centered nonlinear frozen-driver replays using the
same base R_n sequence, while monitoring winner branches and the certified
branch-radius ratio

    chi_n = ||delta x_n|| / rho(x_n).

This is not the full delayed-state variational equation.  In particular it
sets delta R_n = 0.  Phase, history, and EMA feedback are downstream Stage B
work if this reduced cocycle is insufficient.
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
import AIEF_1_4_component_controller_audit as component_audit
import AIEF_1_4_exceptional_K3_transition_audit as k3_audit
import AIEF_1_4_actual_admissibility_branch_audit as branch_audit


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_frozen_driver_cocycle"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_BOUNDARY_TOL = 1e-9
DEFAULT_SUPPORT_TOL = 1e-14
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_SAMPLE_STRIDE = 10
DEFAULT_AMPLITUDE_FRACTIONS = "1e-3,1e-2,1e-1"
DEFAULT_WINDOW_TIMES = "0.1,1,10,50"
DEFAULT_WINDOW_START_STRIDE = 100
DEFAULT_DIRECTION_COUNT = 2
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
    if not values or any(item <= 0.0 for item in values):
        raise argparse.ArgumentTypeError("all values must be positive")
    return sorted(set(values))


def json_compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def frozen_weight_branch(
    B: np.ndarray,
    R: np.ndarray,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    scale_epsilon: float,
) -> dict[str, Any]:
    """Proposal and actual admissibility branch with R held exogenous."""
    dt = float(model["dt"])
    eta = float(model["eta"])
    mu = float(model["mu"])
    gamma = float(model["gamma"])
    F_matrix = (eta + mu) * R - mu - gamma * B
    F_matrix = 0.5 * (F_matrix + F_matrix.T)
    np.fill_diagonal(F_matrix, 0.0)

    proposal = B + dt * F_matrix
    proposal = np.maximum(proposal, 0.0)
    proposal = 0.5 * (proposal + proposal.T)
    np.fill_diagonal(proposal, 0.0)
    x = proposal[edges].copy()
    q_gate = A @ x
    q_scale = np.sum(proposal, axis=1)
    violating = q_gate > capacities
    gate_on = bool(np.any(violating))
    if gate_on:
        scales = np.minimum(1.0, capacities / (q_scale + scale_epsilon))
        edge_scales = np.minimum(scales[edges[0]], scales[edges[1]])
        projected = proposal * np.minimum.outer(scales, scales)
        np.fill_diagonal(projected, 0.0)
    else:
        scales = np.ones(len(capacities), dtype=float)
        edge_scales = np.ones(len(x), dtype=float)
        projected = proposal.copy()
    clipped = gate_on & (scales < 1.0)
    winner_code = np.full(len(x), -1, dtype=int)
    winner_margin = np.abs(scales[edges[0]] - scales[edges[1]])
    for edge, (i_raw, j_raw) in enumerate(zip(edges[0], edges[1])):
        i = int(i_raw)
        j = int(j_raw)
        if not gate_on or (scales[i] == 1.0 and scales[j] == 1.0):
            winner_code[edge] = -1
        elif scales[i] < scales[j]:
            winner_code[edge] = i
        elif scales[j] < scales[i]:
            winner_code[edge] = j
        else:
            winner_code[edge] = -2
    return {
        "F_matrix": F_matrix,
        "x": x,
        "q_gate": q_gate,
        "q_scale": q_scale,
        "violating": violating,
        "gate_on": gate_on,
        "scales": scales,
        "clipped": clipped,
        "edge_scales": edge_scales,
        "winner_code": winner_code,
        "winner_margin": winner_margin,
        "projected": projected,
    }


def selected_branch_jacobian_from_matrix_sums(
    branch: dict[str, Any],
    selected_edges: np.ndarray,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    scale_epsilon: float,
) -> tuple[np.ndarray, bool]:
    """Exact strict-winner selected Jacobian using executed matrix row sums."""
    x = branch["x"]
    q = branch["q_scale"]
    scales = branch["scales"]
    if not branch["gate_on"]:
        return np.eye(len(selected_edges)), True
    J = np.zeros((len(selected_edges), len(selected_edges)), dtype=float)
    classical = True
    for local_row, edge_raw in enumerate(selected_edges):
        edge = int(edge_raw)
        i, j = branch_audit.edge_pair(edge, edges)
        if scales[i] == 1.0 and scales[j] == 1.0:
            J[local_row, local_row] = 1.0
            continue
        if scales[i] < scales[j]:
            winner = i
        elif scales[j] < scales[i]:
            winner = j
        else:
            J[local_row, :] = np.nan
            classical = False
            continue
        scale = scales[winner]
        J[local_row, local_row] = scale
        J[local_row, :] -= (
            x[edge] * scale / (q[winner] + scale_epsilon)
        ) * A[winner, selected_edges]
    return J, classical


def face_lineality_directions(
    split_B: np.ndarray,
    k3_nodes: np.ndarray,
    k3_edges: np.ndarray,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    boundary_tolerance: float,
    direction_count: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Deterministic K3 directions in the split classifier-face lineality."""
    w = split_B[edges]
    saturated = (capacities - A @ w) <= boundary_tolerance
    active_k3 = k3_nodes[saturated[k3_nodes]]
    C = A[np.ix_(active_k3, k3_edges)]
    if C.size:
        _, singular_values, vh = np.linalg.svd(C, full_matrices=True)
        rank = int(np.sum(singular_values > 1e-10))
        basis = vh[rank:].T
    else:
        basis = np.eye(len(k3_edges))
    count = min(direction_count, basis.shape[1])
    if count == 0:
        raise RuntimeError("no K3 face-lineality directions")
    directions = basis[:, :count].copy()
    for column in range(count):
        norm = np.linalg.norm(directions[:, column])
        if norm <= ZERO_TOL:
            raise RuntimeError("degenerate lineality direction")
        directions[:, column] /= norm
        # Deterministic sign convention.
        first = np.flatnonzero(np.abs(directions[:, column]) > 1e-12)
        if len(first) and directions[first[0], column] < 0.0:
            directions[:, column] *= -1.0
    return directions, active_k3


def maximum_symmetric_feasible_amplitude(
    w: np.ndarray,
    direction: np.ndarray,
    A: np.ndarray,
    capacities: np.ndarray,
    zero_tolerance: float = 1e-11,
) -> float:
    """Maximum a with w +/- a d nonnegative and capacity-feasible."""
    limits: list[float] = []
    nonzero = np.abs(direction) > zero_tolerance
    if np.any(nonzero):
        limits.extend((w[nonzero] / np.abs(direction[nonzero])).tolist())
    row_direction = A @ direction
    slack = capacities - A @ w
    changing = np.abs(row_direction) > zero_tolerance
    for node in np.flatnonzero(changing):
        limits.append(float(max(slack[node], 0.0) / abs(row_direction[node])))
    positive = [value for value in limits if np.isfinite(value) and value >= 0.0]
    return float(min(positive)) if positive else np.inf


def branch_signature(branch: dict[str, Any], selected_edges: np.ndarray) -> str:
    return json_compact(
        {
            "gate": int(branch["gate_on"]),
            "winners": branch["winner_code"][selected_edges].astype(int).tolist(),
        }
    )


def matrix_diagnostics(
    K: np.ndarray,
    previous: np.ndarray | None,
) -> dict[str, float]:
    singular_values = np.linalg.svd(K, compute_uv=False)
    eigenvalues = np.linalg.eigvals(K)
    norm = float(singular_values[0])
    nonnormality = float(np.linalg.norm(K.T @ K - K @ K.T))
    nonnormality_relative = nonnormality / max(norm**2, ZERO_TOL)
    if previous is None:
        variation = np.nan
        commutator = np.nan
        commutator_relative = np.nan
    else:
        variation = float(np.linalg.norm(K - previous))
        comm = K @ previous - previous @ K
        commutator = float(np.linalg.norm(comm))
        commutator_relative = commutator / max(
            np.linalg.norm(K) * np.linalg.norm(previous), ZERO_TOL
        )
    return {
        "operator_norm": norm,
        "minimum_singular_value": float(singular_values[-1]),
        "condition_number": float(
            singular_values[0] / singular_values[-1]
        ) if singular_values[-1] > 0.0 else np.inf,
        "spectral_radius": float(np.max(np.abs(eigenvalues))),
        "nonnormality": nonnormality,
        "nonnormality_relative": nonnormality_relative,
        "variation_from_previous": variation,
        "adjacent_commutator": commutator,
        "adjacent_commutator_relative": commutator_relative,
    }


def propagator_diagnostics(U: np.ndarray, elapsed_time: float) -> dict[str, Any]:
    left, singular_values, right_t = np.linalg.svd(U)
    del left
    if elapsed_time > 0.0:
        ftle = np.log(np.maximum(singular_values, np.finfo(float).tiny)) / elapsed_time
    else:
        ftle = np.zeros_like(singular_values)
    condition = (
        float(singular_values[0] / singular_values[-1])
        if singular_values[-1] > 0.0
        else np.inf
    )
    return {
        "singular_values": singular_values,
        "finite_time_exponents": ftle,
        "amplification": float(singular_values[0]),
        "condition_number": condition,
        "principal_initial_vector": right_t[0].copy(),
    }


def sampled_sliding_windows(
    matrices: np.ndarray,
    dt: float,
    window_times: list[float],
    start_stride: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    total_steps = len(matrices)
    for window_time in window_times:
        window_steps = max(1, int(round(window_time / dt)))
        if window_steps > total_steps:
            continue
        for start in range(0, total_steps - window_steps + 1, start_stride):
            U = np.eye(matrices.shape[1])
            for step in range(start, start + window_steps):
                U = matrices[step] @ U
            diagnostics = propagator_diagnostics(U, window_steps * dt)
            singular = diagnostics["singular_values"]
            ftle = diagnostics["finite_time_exponents"]
            rows.append(
                {
                    "window_time": window_steps * dt,
                    "window_steps": window_steps,
                    "start_step": start,
                    "start_time": start * dt,
                    "end_step": start + window_steps,
                    "end_time": (start + window_steps) * dt,
                    "amplification": diagnostics["amplification"],
                    "minimum_singular_value": float(singular[-1]),
                    "condition_number": diagnostics["condition_number"],
                    "principal_finite_time_exponent": float(ftle[0]),
                    "minimum_finite_time_exponent": float(ftle[-1]),
                    "principal_initial_vector_json": json_compact(
                        diagnostics["principal_initial_vector"].tolist()
                    ),
                }
            )
    return pd.DataFrame(rows)


def make_report(
    step_frame: pd.DataFrame,
    propagator_frame: pd.DataFrame,
    window_frame: pd.DataFrame,
    comparison_frame: pd.DataFrame,
    summary_frame: pd.DataFrame,
    *,
    seed: str,
    k3_nodes: np.ndarray,
    k3_edges: np.ndarray,
    active_k3_nodes: np.ndarray,
    final_replay_exact: bool,
    final_replay_max_error: float,
) -> str:
    final_prop = propagator_frame.iloc[-1]
    lines = [
        "AIEF exceptional K3 frozen-driver cocycle analysis",
        "===================================================",
        "",
        "Identity and scope",
        "------------------",
        f"Seed: {seed}",
        f"K3 nodes: {k3_nodes.tolist()}",
        f"K3 edges: {k3_edges.tolist()}",
        f"Split classifier-active K3 nodes: {active_k3_nodes.tolist()}",
        f"Cocycle steps: {len(step_frame)}",
        f"Final base replay exact: {final_replay_exact}",
        f"Final base replay maximum error: {final_replay_max_error:.6g}",
        "* This is the frozen-driver weight subsystem: delta R is set to zero.",
        "",
        "Local matrix sequence",
        "---------------------",
        f"All selected classical Jacobians available: {bool(step_frame['classical_jacobian_available'].all())}",
        f"Winner-signature changes: {int(step_frame['winner_signature_changed'].sum())}",
        f"Maximum ||K[n+1]-K[n]||: {step_frame['variation_from_previous'].max():.6g}",
        f"Median adjacent commutator relative norm: {step_frame['adjacent_commutator_relative'].median():.6g}",
        f"Maximum adjacent commutator relative norm: {step_frame['adjacent_commutator_relative'].max():.6g}",
        f"Maximum instantaneous operator norm: {step_frame['operator_norm'].max():.6g}",
        f"Maximum instantaneous nonnormality relative: {step_frame['nonnormality_relative'].max():.6g}",
        "",
        "From-split propagator",
        "---------------------",
        f"Final time: {final_prop['time']:.6g}",
        f"Final amplification sigma_max: {final_prop['amplification']:.6g}",
        f"Peak from-split amplification: {propagator_frame['amplification'].max():.6g}",
        f"Peak amplification time: {propagator_frame.loc[propagator_frame['amplification'].idxmax(), 'time']:.6g}",
        f"Final condition number: {final_prop['condition_number']:.6g}",
        f"Maximum sampled condition number: {propagator_frame['condition_number'].max():.6g}",
        f"Final principal finite-time exponent: {final_prop['principal_finite_time_exponent']:.6g}",
        f"Final minimum finite-time exponent: {final_prop['minimum_finite_time_exponent']:.6g}",
        f"Final split-lineality restricted amplification: {final_prop['restricted_amplification']:.6g}",
        f"Peak split-lineality restricted amplification: {propagator_frame['restricted_amplification'].max():.6g}",
        f"Final restricted condition number: {final_prop['restricted_condition_number']:.6g}",
        f"Final restricted principal finite-time exponent: {final_prop['restricted_principal_finite_time_exponent']:.6g}",
        "",
        "Sliding-window amplification",
        "----------------------------",
    ]
    if len(window_frame):
        for window_time, group in window_frame.groupby("window_time"):
            peak = group.loc[group["amplification"].idxmax()]
            lines.append(
                f"  window={window_time:.6g}: peak G={peak['amplification']:.6g}, "
                f"start={peak['start_time']:.6g}, end={peak['end_time']:.6g}, "
                f"peak condition={group['condition_number'].max():.6g}"
            )
    else:
        lines.append("  no sliding windows computed")

    lines.extend(["", "Centered nonlinear frozen-driver comparisons", "--------------------------------------------"])
    if len(summary_frame):
        for _, row in summary_frame.iterrows():
            lines.append(
                f"  direction={int(row['direction_id'])}, fraction={row['amplitude_fraction']:.3g}, "
                f"amplitude={row['amplitude']:.3g}, all_branch_preserved={bool(row['all_branch_preserved'])}, "
                f"max_chi={row['maximum_chi']:.3g}, resolved={int(row['resolved_sample_count'])}, "
                f"last_resolved_time={row['last_resolved_time']:.3g}, "
                f"median_error={row['median_relative_error']:.3g}, "
                f"last_resolved_error={row['last_resolved_relative_error']:.3g}"
            )
    else:
        lines.append("  no feasible centered perturbations")

    valid = comparison_frame.loc[
        comparison_frame["reliable_relative_error"].notna()
    ]
    if len(valid):
        lines.extend(
            [
                "",
                f"Overall resolved comparison median relative error: {valid['reliable_relative_error'].median():.6g}",
                f"Overall resolved comparison maximum relative error: {valid['reliable_relative_error'].max():.6g}",
            ]
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Finite-time exponents are not asserted to be asymptotic Oseledets exponents.",
            "* From-split amplification can miss bursts that begin later; sampled sliding windows are also reported.",
            "* Low rank identifies where admissibility coupling lives; it does not imply weak dynamical effect.",
            "* Branch preservation is monitored dynamically for both centered perturbations.",
            "* The base winner branch can be fixed while finite-amplitude perturbed branches cross.",
            "* Failure of the frozen-driver cocycle would motivate the full phase/history/EMA tangent system.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", default=DEFAULT_SEED)
    parser.add_argument("--boundary-tol", type=float, default=DEFAULT_BOUNDARY_TOL)
    parser.add_argument("--support-tol", type=float, default=DEFAULT_SUPPORT_TOL)
    parser.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON)
    parser.add_argument("--sample-stride", type=int, default=DEFAULT_SAMPLE_STRIDE)
    parser.add_argument(
        "--amplitude-fractions",
        type=parse_positive_float_list,
        default=parse_positive_float_list(DEFAULT_AMPLITUDE_FRACTIONS),
    )
    parser.add_argument(
        "--window-times",
        type=parse_positive_float_list,
        default=parse_positive_float_list(DEFAULT_WINDOW_TIMES),
    )
    parser.add_argument(
        "--window-start-stride", type=int, default=DEFAULT_WINDOW_START_STRIDE
    )
    parser.add_argument("--directions", type=int, default=DEFAULT_DIRECTION_COUNT)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(args.boundary_tol, args.support_tol, args.scale_epsilon) <= 0.0:
        raise ValueError("tolerances and epsilon must be positive")
    if min(args.sample_stride, args.window_start_stride, args.directions) <= 0:
        raise ValueError("stride and direction counts must be positive")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    model = manifest["model"]
    node_count = int(model["N"])
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(node_count, capacity, dtype=float)
    A, edges = base.incidence_matrix(node_count)
    dt = float(model["dt"])
    gamma = float(model["gamma"])
    future_steps = int(manifest["protocol"]["future_steps"])

    with np.load(args.npz, allow_pickle=False) as data:
        split_state = base.load_split_state(data, args.seed)
        expected_final = np.asarray(
            data[base.branch_key("continue", args.seed, "B_final")], dtype=float
        ).copy()

    k3_nodes, k3_edges, k3_identification = k3_audit.identify_partial_K3(
        split_state,
        model,
        capacities,
        A,
        edges,
        args.boundary_tol,
        args.support_tol,
    )
    directions, active_k3_nodes = face_lineality_directions(
        split_state.B,
        k3_nodes,
        k3_edges,
        capacities,
        A,
        edges,
        args.boundary_tol,
        args.directions,
    )

    split_w = split_state.B[edges].copy()
    local_split_w = split_w[k3_edges]
    perturbations: list[dict[str, Any]] = []
    for direction_id in range(directions.shape[1]):
        local_direction = directions[:, direction_id]
        full_direction = np.zeros(len(split_w), dtype=float)
        full_direction[k3_edges] = local_direction
        maximum = maximum_symmetric_feasible_amplitude(
            split_w, full_direction, A, capacities
        )
        for fraction in args.amplitude_fractions:
            amplitude = fraction * maximum
            if not np.isfinite(amplitude) or amplitude <= 1e-14:
                continue
            plus_w = split_w + amplitude * full_direction
            minus_w = split_w - amplitude * full_direction
            plus_B = base.vector_to_matrix(plus_w, node_count, edges)
            minus_B = base.vector_to_matrix(minus_w, node_count, edges)
            perturbations.append(
                {
                    "direction_id": direction_id,
                    "direction": local_direction.copy(),
                    "full_direction": full_direction,
                    "amplitude_fraction": fraction,
                    "amplitude": amplitude,
                    "maximum_symmetric_amplitude": maximum,
                    "plus_B": plus_B,
                    "minus_B": minus_B,
                    "linear_vector": local_direction.copy(),
                    "all_branch_preserved": True,
                    "maximum_chi": 0.0,
                }
            )

    state = split_state.clone()
    matrices = np.empty((future_steps, len(k3_edges), len(k3_edges)), dtype=float)
    step_rows: list[dict[str, Any]] = []
    propagator_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    U = np.eye(len(k3_edges))
    qr_Q = np.eye(len(k3_edges))
    qr_log_diagonal = np.zeros(len(k3_edges))
    previous_K: np.ndarray | None = None
    previous_winner_signature: str | None = None

    # Initial propagator diagnostics.
    initial_diag = propagator_diagnostics(U, 0.0)
    initial_restricted = propagator_diagnostics(U @ directions, 0.0)
    propagator_rows.append(
        {
            "step": 0,
            "time": 0.0,
            "amplification": initial_diag["amplification"],
            "minimum_singular_value": float(initial_diag["singular_values"][-1]),
            "condition_number": initial_diag["condition_number"],
            "principal_finite_time_exponent": 0.0,
            "middle_finite_time_exponent": 0.0,
            "minimum_finite_time_exponent": 0.0,
            "restricted_amplification": initial_restricted["amplification"],
            "restricted_minimum_singular_value": float(
                initial_restricted["singular_values"][-1]
            ),
            "restricted_condition_number": initial_restricted["condition_number"],
            "restricted_principal_finite_time_exponent": 0.0,
            "restricted_minimum_finite_time_exponent": 0.0,
            "restricted_principal_initial_coefficients_json": json_compact(
                initial_restricted["principal_initial_vector"].tolist()
            ),
            "QR_rates_json": json_compact([0.0] * len(k3_edges)),
            "principal_initial_vector_json": json_compact(
                initial_diag["principal_initial_vector"].tolist()
            ),
        }
    )

    for step in range(future_steps + 1):
        R_matrix, _, _ = base.compute_field_and_updated_coherence(state, model)
        base_branch = frozen_weight_branch(
            state.B,
            R_matrix,
            model,
            capacities,
            A,
            edges,
            args.scale_epsilon,
        )
        base_signature = branch_signature(base_branch, k3_edges)
        radius, radius_parts = branch_audit.certified_subspace_branch_radius(
            base_branch["x"],
            capacities,
            A,
            edges,
            k3_edges,
            args.scale_epsilon,
        )

        if step < future_steps:
            J_A, classical = selected_branch_jacobian_from_matrix_sums(
                base_branch,
                k3_edges,
                capacities,
                A,
                edges,
                args.scale_epsilon,
            )
            K = (1.0 - gamma * dt) * J_A
            matrices[step] = K
            diagnostics = matrix_diagnostics(K, previous_K)
            winner_changed = (
                previous_winner_signature is not None
                and base_signature != previous_winner_signature
            )
            step_rows.append(
                {
                    "step": step,
                    "time": step * dt,
                    "classical_jacobian_available": classical,
                    "winner_signature": base_signature,
                    "winner_signature_changed": winner_changed,
                    "certified_branch_radius": radius,
                    "radius_positivity": radius_parts["positivity"],
                    "radius_global_gate": radius_parts["global_gate"],
                    "radius_scale_clipping": radius_parts["scale_clipping"],
                    "radius_winner": radius_parts["winner"],
                    "scales_json": json_compact(base_branch["scales"][k3_nodes].tolist()),
                    "winners_json": json_compact(
                        [
                            branch_audit.winner_label(
                                int(base_branch["winner_code"][edge])
                            )
                            for edge in k3_edges
                        ]
                    ),
                    **diagnostics,
                }
            )

        # Compare current centered nonlinear perturbations with current linear vectors.
        if step % args.sample_stride == 0 or step == future_steps:
            base_local_w = state.B[edges][k3_edges]
            for perturbation in perturbations:
                plus_branch = frozen_weight_branch(
                    perturbation["plus_B"],
                    R_matrix,
                    model,
                    capacities,
                    A,
                    edges,
                    args.scale_epsilon,
                )
                minus_branch = frozen_weight_branch(
                    perturbation["minus_B"],
                    R_matrix,
                    model,
                    capacities,
                    A,
                    edges,
                    args.scale_epsilon,
                )
                plus_signature = branch_signature(plus_branch, k3_edges)
                minus_signature = branch_signature(minus_branch, k3_edges)
                branch_preserved = (
                    plus_signature == base_signature
                    and minus_signature == base_signature
                )
                perturbation["all_branch_preserved"] &= branch_preserved
                proposal_delta = max(
                    float(
                        np.linalg.norm(
                            plus_branch["x"][k3_edges]
                            - base_branch["x"][k3_edges]
                        )
                    ),
                    float(
                        np.linalg.norm(
                            minus_branch["x"][k3_edges]
                            - base_branch["x"][k3_edges]
                        )
                    ),
                )
                chi = proposal_delta / max(radius, np.finfo(float).tiny)
                perturbation["maximum_chi"] = max(
                    perturbation["maximum_chi"], chi
                )
                plus_local = perturbation["plus_B"][edges][k3_edges]
                minus_local = perturbation["minus_B"][edges][k3_edges]
                centered = (plus_local - minus_local) / (
                    2.0 * perturbation["amplitude"]
                )
                linear = perturbation["linear_vector"]
                absolute_error = float(np.linalg.norm(centered - linear))
                linear_norm = float(np.linalg.norm(linear))
                relative_error = float(
                    absolute_error / max(linear_norm, ZERO_TOL)
                )
                centered_difference_norm = float(np.linalg.norm(plus_local - minus_local))
                resolution_floor = float(
                    100.0
                    * np.finfo(float).eps
                    * max(np.linalg.norm(base_local_w), 1.0)
                )
                numerically_resolved = bool(
                    centered_difference_norm > resolution_floor
                    and 2.0 * perturbation["amplitude"] * linear_norm
                    > resolution_floor
                )
                nonlinear_distance = float(
                    max(
                        np.linalg.norm(plus_local - base_local_w),
                        np.linalg.norm(minus_local - base_local_w),
                    )
                )
                comparison_rows.append(
                    {
                        "step": step,
                        "time": step * dt,
                        "direction_id": perturbation["direction_id"],
                        "amplitude_fraction": perturbation["amplitude_fraction"],
                        "amplitude": perturbation["amplitude"],
                        "maximum_symmetric_amplitude": perturbation[
                            "maximum_symmetric_amplitude"
                        ],
                        "branch_preserved": branch_preserved,
                        "plus_signature": plus_signature,
                        "base_signature": base_signature,
                        "minus_signature": minus_signature,
                        "certified_branch_radius": radius,
                        "proposal_delta_norm": proposal_delta,
                        "chi": chi,
                        "linear_norm": linear_norm,
                        "centered_nonlinear_norm": float(np.linalg.norm(centered)),
                        "centered_difference_norm": centered_difference_norm,
                        "resolution_floor": resolution_floor,
                        "numerically_resolved": numerically_resolved,
                        "nonlinear_distance_from_base": nonlinear_distance,
                        "absolute_error": absolute_error,
                        "relative_error": relative_error,
                        "reliable_relative_error": relative_error
                        if numerically_resolved
                        else np.nan,
                    }
                )

        if step == future_steps:
            break

        # Advance nonlinear frozen-driver perturbations with the same base R_n.
        for perturbation in perturbations:
            plus_branch = frozen_weight_branch(
                perturbation["plus_B"],
                R_matrix,
                model,
                capacities,
                A,
                edges,
                args.scale_epsilon,
            )
            minus_branch = frozen_weight_branch(
                perturbation["minus_B"],
                R_matrix,
                model,
                capacities,
                A,
                edges,
                args.scale_epsilon,
            )
            # Branch preservation and chi are audited at every step, not only
            # at output sample times.
            plus_signature = branch_signature(plus_branch, k3_edges)
            minus_signature = branch_signature(minus_branch, k3_edges)
            perturbation["all_branch_preserved"] &= bool(
                plus_signature == base_signature
                and minus_signature == base_signature
            )
            proposal_delta = max(
                float(
                    np.linalg.norm(
                        plus_branch["x"][k3_edges]
                        - base_branch["x"][k3_edges]
                    )
                ),
                float(
                    np.linalg.norm(
                        minus_branch["x"][k3_edges]
                        - base_branch["x"][k3_edges]
                    )
                ),
            )
            chi = proposal_delta / max(radius, np.finfo(float).tiny)
            perturbation["maximum_chi"] = max(
                perturbation["maximum_chi"], chi
            )
            perturbation["plus_B"] = plus_branch["projected"]
            perturbation["minus_B"] = minus_branch["projected"]
            perturbation["linear_vector"] = K @ perturbation["linear_vector"]

        # Advance the exact base coupled replay, which supplies R_{n+1} next step.
        base.actual_step(
            state,
            model,
            capacities,
            A,
            edges,
            args.boundary_tol,
            audit_operator=False,
        )

        # Propagator and QR updates.
        U = K @ U
        qr_Z = K @ qr_Q
        qr_Q, qr_R = np.linalg.qr(qr_Z)
        qr_log_diagonal += np.log(
            np.maximum(np.abs(np.diag(qr_R)), np.finfo(float).tiny)
        )
        elapsed = (step + 1) * dt
        if (step + 1) % args.sample_stride == 0 or step + 1 == future_steps:
            diagnostics = propagator_diagnostics(U, elapsed)
            restricted = propagator_diagnostics(U @ directions, elapsed)
            singular = diagnostics["singular_values"]
            ftle = diagnostics["finite_time_exponents"]
            restricted_singular = restricted["singular_values"]
            restricted_ftle = restricted["finite_time_exponents"]
            qr_rates = qr_log_diagonal / elapsed
            propagator_rows.append(
                {
                    "step": step + 1,
                    "time": elapsed,
                    "amplification": diagnostics["amplification"],
                    "minimum_singular_value": float(singular[-1]),
                    "condition_number": diagnostics["condition_number"],
                    "principal_finite_time_exponent": float(ftle[0]),
                    "middle_finite_time_exponent": float(ftle[1]),
                    "minimum_finite_time_exponent": float(ftle[-1]),
                    "restricted_amplification": restricted["amplification"],
                    "restricted_minimum_singular_value": float(
                        restricted_singular[-1]
                    ),
                    "restricted_condition_number": restricted["condition_number"],
                    "restricted_principal_finite_time_exponent": float(
                        restricted_ftle[0]
                    ),
                    "restricted_minimum_finite_time_exponent": float(
                        restricted_ftle[-1]
                    ),
                    "restricted_principal_initial_coefficients_json": json_compact(
                        restricted["principal_initial_vector"].tolist()
                    ),
                    "QR_rates_json": json_compact(qr_rates.tolist()),
                    "principal_initial_vector_json": json_compact(
                        diagnostics["principal_initial_vector"].tolist()
                    ),
                }
            )
        previous_K = K.copy()
        previous_winner_signature = base_signature

    final_replay_exact = bool(np.array_equal(state.B, expected_final))
    final_replay_max_error = float(np.max(np.abs(state.B - expected_final)))

    step_frame = pd.DataFrame(step_rows)
    propagator_frame = pd.DataFrame(propagator_rows)
    comparison_frame = pd.DataFrame(comparison_rows)
    window_frame = sampled_sliding_windows(
        matrices,
        dt,
        args.window_times,
        args.window_start_stride,
    )

    summary_rows: list[dict[str, Any]] = []
    for perturbation in perturbations:
        group = comparison_frame.loc[
            (comparison_frame["direction_id"] == perturbation["direction_id"])
            & (
                comparison_frame["amplitude_fraction"]
                == perturbation["amplitude_fraction"]
            )
        ]
        finite = group.loc[group["reliable_relative_error"].notna()]
        summary_rows.append(
            {
                "direction_id": perturbation["direction_id"],
                "direction_json": json_compact(
                    perturbation["direction"].tolist()
                ),
                "amplitude_fraction": perturbation["amplitude_fraction"],
                "amplitude": perturbation["amplitude"],
                "maximum_symmetric_amplitude": perturbation[
                    "maximum_symmetric_amplitude"
                ],
                "all_branch_preserved": perturbation[
                    "all_branch_preserved"
                ],
                "maximum_chi": perturbation["maximum_chi"],
                "resolved_sample_count": int(len(finite)),
                "last_resolved_time": float(finite.iloc[-1]["time"])
                if len(finite)
                else np.nan,
                "median_relative_error": float(
                    finite["reliable_relative_error"].median()
                )
                if len(finite)
                else np.nan,
                "maximum_relative_error": float(
                    finite["reliable_relative_error"].max()
                )
                if len(finite)
                else np.nan,
                "last_resolved_relative_error": float(
                    finite.iloc[-1]["reliable_relative_error"]
                )
                if len(finite)
                else np.nan,
                "last_resolved_linear_norm": float(finite.iloc[-1]["linear_norm"])
                if len(finite)
                else np.nan,
                "last_resolved_centered_nonlinear_norm": float(
                    finite.iloc[-1]["centered_nonlinear_norm"]
                )
                if len(finite)
                else np.nan,
            }
        )
    summary_frame = pd.DataFrame(summary_rows)

    component_audit.atomic_write_csv(
        output_dir / "frozen_cocycle_step_diagnostics.csv", step_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "frozen_cocycle_propagator.csv", propagator_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "frozen_cocycle_sliding_windows.csv", window_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "frozen_cocycle_nonlinear_comparison.csv", comparison_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "frozen_cocycle_nonlinear_summary.csv", summary_frame
    )
    component_audit.atomic_savez(
        output_dir / "frozen_cocycle_matrices.npz",
        {
            "K3_matrix_sequence": matrices,
            "K3_direction_basis": directions,
            "K3_nodes": k3_nodes,
            "K3_edges": k3_edges,
        },
    )

    report = make_report(
        step_frame,
        propagator_frame,
        window_frame,
        comparison_frame,
        summary_frame,
        seed=args.seed,
        k3_nodes=k3_nodes,
        k3_edges=k3_edges,
        active_k3_nodes=active_k3_nodes,
        final_replay_exact=final_replay_exact,
        final_replay_max_error=final_replay_max_error,
    )
    component_audit.atomic_write_text(
        output_dir / "frozen_driver_cocycle_report.txt", report
    )

    source_path = Path(__file__).resolve()
    dependencies = {
        "stationarity": Path(base.__file__).resolve(),
        "component_audit": Path(component_audit.__file__).resolve(),
        "K3_audit": Path(k3_audit.__file__).resolve(),
        "branch_audit": Path(branch_audit.__file__).resolve(),
    }
    analysis_manifest = {
        "analysis": "AIEF-1.4 exceptional K3 frozen-driver finite-time cocycle",
        "source": {"path": str(source_path), "sha256": file_sha256(source_path)},
        "dependencies": {
            name: {"path": str(path), "sha256": file_sha256(path)}
            for name, path in dependencies.items()
        },
        "command": sys.argv,
        "inputs": {
            "npz": {
                "path": str(Path(args.npz).resolve()),
                "sha256": file_sha256(args.npz),
            },
            "manifest": {
                "path": str(Path(args.manifest).resolve()),
                "sha256": file_sha256(args.manifest),
            },
        },
        "seed": args.seed,
        "K3_nodes": k3_nodes.tolist(),
        "K3_edges": k3_edges.tolist(),
        "K3_identification": k3_identification,
        "split_classifier_active_K3_nodes": active_k3_nodes.tolist(),
        "dt": dt,
        "future_steps": future_steps,
        "scale_epsilon": args.scale_epsilon,
        "boundary_tolerance": args.boundary_tol,
        "support_tolerance": args.support_tol,
        "sample_stride": args.sample_stride,
        "amplitude_fractions": args.amplitude_fractions,
        "window_times": args.window_times,
        "window_start_stride": args.window_start_stride,
        "direction_count": directions.shape[1],
        "final_replay_exact": final_replay_exact,
        "final_replay_max_error": final_replay_max_error,
        "outputs": [
            "frozen_cocycle_step_diagnostics.csv",
            "frozen_cocycle_propagator.csv",
            "frozen_cocycle_sliding_windows.csv",
            "frozen_cocycle_nonlinear_comparison.csv",
            "frozen_cocycle_nonlinear_summary.csv",
            "frozen_cocycle_matrices.npz",
            "frozen_driver_cocycle_report.txt",
        ],
        "interpretation_constraints": [
            "This is the frozen-driver weight subsystem with delta R set to zero.",
            "Finite-time exponents are not asserted to be asymptotic Lyapunov exponents.",
            "The base winner branch can remain fixed while finite-amplitude perturbed branches cross.",
            "Low rank locates node-mediated coupling but does not bound its dynamical importance.",
            "A failed frozen-driver comparison motivates, but does not itself identify, delayed-state feedback.",
            "This is one deterministic frozen seed, not independent population evidence.",
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
