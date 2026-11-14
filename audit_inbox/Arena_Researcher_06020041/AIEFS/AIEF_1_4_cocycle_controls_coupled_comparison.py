#!/usr/bin/env python3
"""Stable cocycle controls and coupled-vs-frozen comparison for AIEF-1.4.

This script consumes the frozen-driver K3 matrix sequence and performs the
next two targeted analyses without launching a new seed cohort:

A. Numerical/operator controls
   * underflow-resistant log singular values using first and second compound
     cocycles plus accumulated log determinants;
   * actual K_n versus K_0^n, K_late^n, and a diagonal-scale-only cocycle;
   * dense short sliding-window amplification;
   * log condition numbers and finite-time exponents without forming an
     underflowed smallest singular value.

B. Coupled centered comparison
   * reuses the same K3 directions and feasible amplitude fractions;
   * evolves frozen-driver +/- weight trajectories using the base R_n;
   * evolves fully coupled +/- DynamicState trajectories, including phase,
     delay history, and complex EMA feedback;
   * compares both centered nonlinear derivatives with the frozen-driver
     linear cocycle;
   * monitors winner branches and chi=||delta x||/rho dynamically.

The script does not yet construct the analytic augmented delayed-state
Jacobian.  It tests whether that Stage-B derivation is necessary by directly
measuring the feedback discrepancy between coupled and frozen centered
trajectories.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

import AIEF_1_4_stationarity_perturbation_analysis_updated as base
import AIEF_1_4_component_controller_audit as component_audit
import AIEF_1_4_actual_admissibility_branch_audit as branch_audit
import AIEF_1_4_frozen_driver_cocycle_analysis as frozen


DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = (
    f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
)
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_COCYCLE_NPZ = "aief_1_4_frozen_driver_cocycle/frozen_cocycle_matrices.npz"
DEFAULT_COCYCLE_STEP = "aief_1_4_frozen_driver_cocycle/frozen_cocycle_step_diagnostics.csv"
DEFAULT_OUTPUT_DIR = "aief_1_4_cocycle_controls_coupled"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_BOUNDARY_TOL = 1e-9
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_SAMPLE_STRIDE = 10
DEFAULT_AMPLITUDE_FRACTIONS = "1e-3,1e-2,1e-1"
DEFAULT_DENSE_WINDOW_TIMES = "0.1,1"
DEFAULT_DENSE_WINDOW_START_STRIDE = 1
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
        raise argparse.ArgumentTypeError("values must be positive")
    return sorted(set(values))


def json_compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def compound2(matrix: np.ndarray) -> np.ndarray:
    """Second compound matrix in pair order (01, 02, 12)."""
    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (3, 3):
        raise ValueError("compound2 currently requires a 3x3 matrix")
    pairs = ((0, 1), (0, 2), (1, 2))
    result = np.empty((3, 3), dtype=float)
    for row, row_pair in enumerate(pairs):
        for column, column_pair in enumerate(pairs):
            result[row, column] = np.linalg.det(
                matrix[np.ix_(row_pair, column_pair)]
            )
    return result


def wedge_columns(matrix: np.ndarray) -> np.ndarray:
    """Exterior product of the two columns of a 3x2 matrix."""
    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (3, 2):
        raise ValueError("wedge_columns requires a 3x2 matrix")
    return np.array(
        [
            np.linalg.det(matrix[np.ix_((0, 1), (0, 1))]),
            np.linalg.det(matrix[np.ix_((0, 2), (0, 1))]),
            np.linalg.det(matrix[np.ix_((1, 2), (0, 1))]),
        ],
        dtype=float,
    )


def normalize_matrix(matrix: np.ndarray) -> tuple[np.ndarray, float]:
    norm = float(np.linalg.norm(matrix))
    if norm == 0.0:
        return matrix.copy(), -np.inf
    return matrix / norm, math.log(norm)


def normalize_vector(vector: np.ndarray) -> tuple[np.ndarray, float]:
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        return vector.copy(), -np.inf
    return vector / norm, math.log(norm)


def safe_exp(value: float) -> float:
    if value > math.log(np.finfo(float).max):
        return np.inf
    if value < math.log(np.finfo(float).tiny):
        return 0.0
    return math.exp(value)


def stable_spectrum_sequence(
    matrices: np.ndarray,
    initial_basis: np.ndarray,
    dt: float,
    sample_stride: int,
    label: str,
) -> pd.DataFrame:
    """Stable log singular values for full 3D and a 2D initial subspace."""
    matrices = np.asarray(matrices, dtype=float)
    initial_basis = np.asarray(initial_basis, dtype=float)
    if matrices.ndim != 3 or matrices.shape[1:] != (3, 3):
        raise ValueError("matrix sequence must have shape (steps,3,3)")
    if initial_basis.shape != (3, 2):
        raise ValueError("initial basis must have shape (3,2)")

    P = np.eye(3)
    log_P_scale = 0.0
    C = np.eye(3)
    log_C_scale = 0.0
    log_abs_det = 0.0

    V = initial_basis.copy()
    log_V_scale = 0.0
    wedge = wedge_columns(initial_basis)
    wedge, initial_wedge_log = normalize_vector(wedge)
    log_wedge_scale = initial_wedge_log

    rows: list[dict[str, Any]] = []

    def append_row(step: int) -> None:
        elapsed = step * dt
        singular_P = np.linalg.svd(P, compute_uv=False)
        singular_C = np.linalg.svd(C, compute_uv=False)
        log_sigma1 = log_P_scale + math.log(max(singular_P[0], np.finfo(float).tiny))
        log_sigma12 = log_C_scale + math.log(max(singular_C[0], np.finfo(float).tiny))
        log_sigma2 = log_sigma12 - log_sigma1
        log_sigma3 = log_abs_det - log_sigma12

        singular_V = np.linalg.svd(V, compute_uv=False)
        log_restricted_sigma1 = log_V_scale + math.log(
            max(singular_V[0], np.finfo(float).tiny)
        )
        log_restricted_sigma12 = log_wedge_scale
        log_restricted_sigma2 = (
            log_restricted_sigma12 - log_restricted_sigma1
        )

        if elapsed > 0.0:
            exponents = np.array(
                [log_sigma1, log_sigma2, log_sigma3]
            ) / elapsed
            restricted_exponents = np.array(
                [log_restricted_sigma1, log_restricted_sigma2]
            ) / elapsed
        else:
            exponents = np.zeros(3)
            restricted_exponents = np.zeros(2)
        rows.append(
            {
                "control": label,
                "step": step,
                "time": elapsed,
                "log_sigma1": log_sigma1,
                "log_sigma2": log_sigma2,
                "log_sigma3": log_sigma3,
                "sigma1": safe_exp(log_sigma1),
                "sigma2": safe_exp(log_sigma2),
                "sigma3": safe_exp(log_sigma3),
                "log_condition_number": log_sigma1 - log_sigma3,
                "condition_number": safe_exp(log_sigma1 - log_sigma3),
                "principal_finite_time_exponent": float(exponents[0]),
                "middle_finite_time_exponent": float(exponents[1]),
                "minimum_finite_time_exponent": float(exponents[2]),
                "restricted_log_sigma1": log_restricted_sigma1,
                "restricted_log_sigma2": log_restricted_sigma2,
                "restricted_sigma1": safe_exp(log_restricted_sigma1),
                "restricted_sigma2": safe_exp(log_restricted_sigma2),
                "restricted_log_condition_number": (
                    log_restricted_sigma1 - log_restricted_sigma2
                ),
                "restricted_condition_number": safe_exp(
                    log_restricted_sigma1 - log_restricted_sigma2
                ),
                "restricted_principal_finite_time_exponent": float(
                    restricted_exponents[0]
                ),
                "restricted_minimum_finite_time_exponent": float(
                    restricted_exponents[1]
                ),
            }
        )

    append_row(0)
    for index, matrix in enumerate(matrices):
        P, increment = normalize_matrix(matrix @ P)
        log_P_scale += increment
        C, compound_increment = normalize_matrix(compound2(matrix) @ C)
        log_C_scale += compound_increment
        sign, logdet = np.linalg.slogdet(matrix)
        if sign == 0.0:
            log_abs_det = -np.inf
        elif np.isfinite(log_abs_det):
            log_abs_det += float(logdet)

        V, restricted_increment = normalize_matrix(matrix @ V)
        log_V_scale += restricted_increment
        wedge, wedge_increment = normalize_vector(compound2(matrix) @ wedge)
        log_wedge_scale += wedge_increment

        step = index + 1
        if step % sample_stride == 0 or step == len(matrices):
            append_row(step)
    return pd.DataFrame(rows)


def diagonal_scale_matrices(
    step_frame: pd.DataFrame,
    k3_nodes: np.ndarray,
    k3_edges: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    gamma: float,
    dt: float,
) -> np.ndarray:
    node_position = {int(node): index for index, node in enumerate(k3_nodes)}
    matrices = np.empty((len(step_frame), len(k3_edges), len(k3_edges)))
    factor = 1.0 - gamma * dt
    for row_index, (_, row) in enumerate(step_frame.iterrows()):
        scales = np.asarray(json.loads(row["scales_json"]), dtype=float)
        edge_scales = []
        for edge in k3_edges:
            i, j = branch_audit.edge_pair(int(edge), edges)
            edge_scales.append(
                min(scales[node_position[i]], scales[node_position[j]])
            )
        matrices[row_index] = factor * np.diag(edge_scales)
    return matrices


def constant_sequence(matrix: np.ndarray, length: int) -> np.ndarray:
    return np.broadcast_to(matrix, (length,) + matrix.shape)


def dense_sliding_windows(
    controls: dict[str, np.ndarray],
    dt: float,
    window_times: list[float],
    start_stride: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for label, matrices in controls.items():
        total = len(matrices)
        for requested_time in window_times:
            window_steps = max(1, int(round(requested_time / dt)))
            if window_steps > total:
                continue
            # Constant controls need only one representative start.
            starts: Iterable[int]
            if label in {"K0_constant", "Klate_constant"}:
                starts = [0]
            else:
                starts = range(0, total - window_steps + 1, start_stride)
            for start in starts:
                product = np.eye(3)
                for step in range(start, start + window_steps):
                    product = matrices[step] @ product
                singular = np.linalg.svd(product, compute_uv=False)
                log_singular = np.log(
                    np.maximum(singular, np.finfo(float).tiny)
                )
                elapsed = window_steps * dt
                rows.append(
                    {
                        "control": label,
                        "window_time": elapsed,
                        "window_steps": window_steps,
                        "start_step": start,
                        "start_time": start * dt,
                        "end_step": start + window_steps,
                        "end_time": (start + window_steps) * dt,
                        "amplification": float(singular[0]),
                        "minimum_singular_value": float(singular[-1]),
                        "log_condition_number": float(
                            log_singular[0] - log_singular[-1]
                        ),
                        "principal_finite_time_exponent": float(
                            log_singular[0] / elapsed
                        ),
                    }
                )
    return pd.DataFrame(rows)


def wrapped_phase_centered(
    plus: np.ndarray,
    minus: np.ndarray,
    amplitude: float,
) -> np.ndarray:
    difference = np.angle(np.exp(1j * (plus - minus)))
    return difference / (2.0 * amplitude)


def centered_resolution(
    plus: np.ndarray,
    minus: np.ndarray,
    base_value: np.ndarray,
    amplitude: float,
    linear_norm: float,
) -> tuple[bool, float, float]:
    difference_norm = float(np.linalg.norm(plus - minus))
    floor = float(
        100.0
        * np.finfo(float).eps
        * max(np.linalg.norm(base_value), 1.0)
    )
    resolved = bool(
        difference_norm > floor
        and 2.0 * amplitude * linear_norm > floor
    )
    return resolved, difference_norm, floor


def make_report(
    stable_frame: pd.DataFrame,
    window_frame: pd.DataFrame,
    coupled_frame: pd.DataFrame,
    coupled_summary: pd.DataFrame,
    *,
    seed: str,
    matrix_recompute_error: float,
    final_replay_exact: bool,
    final_replay_max_error: float,
) -> str:
    lines = [
        "AIEF K3 cocycle controls and coupled comparison",
        "================================================",
        "",
        "Identity",
        "--------",
        f"Seed: {seed}",
        f"Recomputed versus saved K-matrix maximum error: {matrix_recompute_error:.6g}",
        f"Final base replay exact: {final_replay_exact}",
        f"Final base replay maximum error: {final_replay_max_error:.6g}",
        "",
        "Stable finite-time singular spectra",
        "------------------------------------",
    ]
    for control, group in stable_frame.groupby("control"):
        final = group.iloc[-1]
        peak = group.loc[group["sigma1"].idxmax()]
        lines.append(
            f"  {control}: peak_sigma1={peak['sigma1']:.6g} at t={peak['time']:.6g}, "
            f"final_lambda1={final['principal_finite_time_exponent']:.6g}, "
            f"final_lambda2={final['middle_finite_time_exponent']:.6g}, "
            f"final_lambda3={final['minimum_finite_time_exponent']:.6g}, "
            f"final_log_kappa={final['log_condition_number']:.6g}, "
            f"restricted_peak={group['restricted_sigma1'].max():.6g}"
        )

    lines.extend(["", "Dense short-window amplification", "--------------------------------"])
    for (control, window_time), group in window_frame.groupby(
        ["control", "window_time"]
    ):
        peak = group.loc[group["amplification"].idxmax()]
        lines.append(
            f"  {control}, window={window_time:.6g}: peak_G={peak['amplification']:.6g}, "
            f"start={peak['start_time']:.6g}, end={peak['end_time']:.6g}"
        )

    lines.extend(["", "Coupled versus frozen centered comparisons", "-------------------------------------------"])
    for _, row in coupled_summary.iterrows():
        lines.append(
            f"  direction={int(row['direction_id'])}, fraction={row['amplitude_fraction']:.3g}, "
            f"amplitude={row['amplitude']:.3g}, frozen_branch={bool(row['all_frozen_branch_preserved'])}, "
            f"coupled_branch={bool(row['all_coupled_branch_preserved'])}, "
            f"max_chi_frozen={row['maximum_frozen_chi']:.3g}, "
            f"max_chi_coupled={row['maximum_coupled_chi']:.3g}, "
            f"resolved={int(row['resolved_sample_count'])}, "
            f"median_frozen_error={row['median_frozen_linear_error']:.3g}, "
            f"median_coupled_error={row['median_coupled_linear_error']:.3g}, "
            f"median_feedback_fraction={row['median_feedback_fraction']:.3g}, "
            f"last_resolved_time={row['last_resolved_time']:.3g}"
        )

    reliable = coupled_frame.loc[coupled_frame["numerically_resolved"]]
    if len(reliable):
        lines.extend(
            [
                "",
                f"Overall resolved median frozen-linear error: {reliable['frozen_linear_relative_error'].median():.6g}",
                f"Overall resolved median coupled-linear error: {reliable['coupled_linear_relative_error'].median():.6g}",
                f"Overall resolved median feedback fraction: {reliable['feedback_fraction'].median():.6g}",
                f"Maximum resolved feedback fraction: {reliable['feedback_fraction'].max():.6g}",
            ]
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* Compound-cocycle exponents are finite-time quantities, not asserted Oseledets limits.",
            "* K0, Klate, and diagonal-only sequences are controlled counterfactuals, not additive causal decompositions.",
            "* Coupled-minus-frozen centered differences measure feedback effects for the tested directions and amplitudes.",
            "* The frozen linear cocycle is a reduced weight-sector model with delta R set to zero.",
            "* Branch preservation is audited dynamically for frozen and fully coupled perturbations.",
            "* A substantial coupled discrepancy motivates an analytic augmented phase/history/EMA tangent model.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--cocycle-npz", default=DEFAULT_COCYCLE_NPZ)
    parser.add_argument("--cocycle-step", default=DEFAULT_COCYCLE_STEP)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", default=DEFAULT_SEED)
    parser.add_argument("--boundary-tol", type=float, default=DEFAULT_BOUNDARY_TOL)
    parser.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON)
    parser.add_argument("--sample-stride", type=int, default=DEFAULT_SAMPLE_STRIDE)
    parser.add_argument(
        "--amplitude-fractions",
        type=parse_positive_float_list,
        default=parse_positive_float_list(DEFAULT_AMPLITUDE_FRACTIONS),
    )
    parser.add_argument(
        "--dense-window-times",
        type=parse_positive_float_list,
        default=parse_positive_float_list(DEFAULT_DENSE_WINDOW_TIMES),
    )
    parser.add_argument(
        "--dense-window-start-stride",
        type=int,
        default=DEFAULT_DENSE_WINDOW_START_STRIDE,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.npz, args.manifest, args.cocycle_npz, args.cocycle_step):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(args.boundary_tol, args.scale_epsilon) <= 0.0:
        raise ValueError("tolerances and epsilon must be positive")
    if min(args.sample_stride, args.dense_window_start_stride) <= 0:
        raise ValueError("strides must be positive")

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

    with np.load(args.cocycle_npz, allow_pickle=False) as data:
        matrices = np.asarray(data["K3_matrix_sequence"], dtype=float).copy()
        directions = np.asarray(data["K3_direction_basis"], dtype=float).copy()
        k3_nodes = np.asarray(data["K3_nodes"], dtype=int).copy()
        k3_edges = np.asarray(data["K3_edges"], dtype=int).copy()
    if matrices.shape != (future_steps, 3, 3):
        raise ValueError(f"unexpected matrix sequence shape {matrices.shape}")
    if directions.shape != (3, 2):
        raise ValueError(f"expected two K3 directions, got {directions.shape}")
    step_source = pd.read_csv(args.cocycle_step)
    if len(step_source) != future_steps:
        raise ValueError("cocycle step CSV length does not match future_steps")

    diagonal_matrices = diagonal_scale_matrices(
        step_source, k3_nodes, k3_edges, edges, gamma, dt
    )
    controls = {
        "actual_time_varying": matrices,
        "K0_constant": constant_sequence(matrices[0], future_steps),
        "Klate_constant": constant_sequence(matrices[-1], future_steps),
        "diagonal_scale_only": diagonal_matrices,
    }
    stable_frames = [
        stable_spectrum_sequence(
            sequence, directions, dt, args.sample_stride, label
        )
        for label, sequence in controls.items()
    ]
    stable_frame = pd.concat(stable_frames, ignore_index=True)
    window_frame = dense_sliding_windows(
        controls,
        dt,
        args.dense_window_times,
        args.dense_window_start_stride,
    )

    with np.load(args.npz, allow_pickle=False) as data:
        split_state = base.load_split_state(data, args.seed)
        expected_final = np.asarray(
            data[base.branch_key("continue", args.seed, "B_final")], dtype=float
        ).copy()

    split_w = split_state.B[edges].copy()
    perturbations: list[dict[str, Any]] = []
    for direction_id in range(directions.shape[1]):
        local_direction = directions[:, direction_id]
        full_direction = np.zeros(len(split_w), dtype=float)
        full_direction[k3_edges] = local_direction
        maximum = frozen.maximum_symmetric_feasible_amplitude(
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
            coupled_plus = split_state.clone()
            coupled_minus = split_state.clone()
            coupled_plus.B = plus_B.copy()
            coupled_minus.B = minus_B.copy()
            perturbations.append(
                {
                    "direction_id": direction_id,
                    "direction": local_direction.copy(),
                    "amplitude_fraction": fraction,
                    "amplitude": amplitude,
                    "maximum_symmetric_amplitude": maximum,
                    "frozen_plus_B": plus_B.copy(),
                    "frozen_minus_B": minus_B.copy(),
                    "coupled_plus": coupled_plus,
                    "coupled_minus": coupled_minus,
                    "linear_vector": local_direction.copy(),
                    "all_frozen_branch_preserved": True,
                    "all_coupled_branch_preserved": True,
                    "maximum_frozen_chi": 0.0,
                    "maximum_coupled_chi": 0.0,
                }
            )

    state = split_state.clone()
    comparison_rows: list[dict[str, Any]] = []
    matrix_recompute_error = 0.0

    for step in range(future_steps + 1):
        base_branch = branch_audit.proposal_and_admissibility_branch(
            state, model, capacities, A, edges, args.scale_epsilon
        )
        R_base = base_branch["R_matrix"]
        base_signature = frozen.branch_signature(base_branch, k3_edges)
        radius, _ = branch_audit.certified_subspace_branch_radius(
            base_branch["x"],
            capacities,
            A,
            edges,
            k3_edges,
            args.scale_epsilon,
        )
        if step < future_steps:
            recomputed_J, classical = frozen.selected_branch_jacobian_from_matrix_sums(
                base_branch,
                k3_edges,
                capacities,
                A,
                edges,
                args.scale_epsilon,
            )
            if not classical:
                raise RuntimeError(f"selected classical Jacobian unavailable at step {step}")
            recomputed_K = (1.0 - gamma * dt) * recomputed_J
            matrix_recompute_error = max(
                matrix_recompute_error,
                float(np.max(np.abs(recomputed_K - matrices[step]))),
            )

        branch_cache: list[dict[str, Any]] = []
        for perturbation in perturbations:
            frozen_plus_branch = frozen.frozen_weight_branch(
                perturbation["frozen_plus_B"],
                R_base,
                model,
                capacities,
                A,
                edges,
                args.scale_epsilon,
            )
            frozen_minus_branch = frozen.frozen_weight_branch(
                perturbation["frozen_minus_B"],
                R_base,
                model,
                capacities,
                A,
                edges,
                args.scale_epsilon,
            )
            coupled_plus_branch = branch_audit.proposal_and_admissibility_branch(
                perturbation["coupled_plus"],
                model,
                capacities,
                A,
                edges,
                args.scale_epsilon,
            )
            coupled_minus_branch = branch_audit.proposal_and_admissibility_branch(
                perturbation["coupled_minus"],
                model,
                capacities,
                A,
                edges,
                args.scale_epsilon,
            )
            frozen_signatures = (
                frozen.branch_signature(frozen_plus_branch, k3_edges),
                frozen.branch_signature(frozen_minus_branch, k3_edges),
            )
            coupled_signatures = (
                frozen.branch_signature(coupled_plus_branch, k3_edges),
                frozen.branch_signature(coupled_minus_branch, k3_edges),
            )
            frozen_preserved = all(
                signature == base_signature for signature in frozen_signatures
            )
            coupled_preserved = all(
                signature == base_signature for signature in coupled_signatures
            )
            perturbation["all_frozen_branch_preserved"] &= frozen_preserved
            perturbation["all_coupled_branch_preserved"] &= coupled_preserved

            frozen_delta_x = max(
                np.linalg.norm(
                    frozen_plus_branch["x"][k3_edges]
                    - base_branch["x"][k3_edges]
                ),
                np.linalg.norm(
                    frozen_minus_branch["x"][k3_edges]
                    - base_branch["x"][k3_edges]
                ),
            )
            coupled_delta_x = max(
                np.linalg.norm(
                    coupled_plus_branch["x"][k3_edges]
                    - base_branch["x"][k3_edges]
                ),
                np.linalg.norm(
                    coupled_minus_branch["x"][k3_edges]
                    - base_branch["x"][k3_edges]
                ),
            )
            frozen_chi = float(
                frozen_delta_x / max(radius, np.finfo(float).tiny)
            )
            coupled_chi = float(
                coupled_delta_x / max(radius, np.finfo(float).tiny)
            )
            perturbation["maximum_frozen_chi"] = max(
                perturbation["maximum_frozen_chi"], frozen_chi
            )
            perturbation["maximum_coupled_chi"] = max(
                perturbation["maximum_coupled_chi"], coupled_chi
            )
            branch_cache.append(
                {
                    "frozen_plus": frozen_plus_branch,
                    "frozen_minus": frozen_minus_branch,
                    "coupled_plus": coupled_plus_branch,
                    "coupled_minus": coupled_minus_branch,
                    "frozen_preserved": frozen_preserved,
                    "coupled_preserved": coupled_preserved,
                    "frozen_chi": frozen_chi,
                    "coupled_chi": coupled_chi,
                }
            )

        if step % args.sample_stride == 0 or step == future_steps:
            base_local = state.B[edges][k3_edges]
            for perturbation, cached in zip(perturbations, branch_cache):
                amplitude = perturbation["amplitude"]
                frozen_plus_local = perturbation["frozen_plus_B"][edges][k3_edges]
                frozen_minus_local = perturbation["frozen_minus_B"][edges][k3_edges]
                coupled_plus_local = perturbation["coupled_plus"].B[edges][k3_edges]
                coupled_minus_local = perturbation["coupled_minus"].B[edges][k3_edges]
                frozen_centered = (frozen_plus_local - frozen_minus_local) / (
                    2.0 * amplitude
                )
                coupled_centered = (coupled_plus_local - coupled_minus_local) / (
                    2.0 * amplitude
                )
                linear = perturbation["linear_vector"]
                linear_norm = float(np.linalg.norm(linear))
                frozen_error = float(np.linalg.norm(frozen_centered - linear))
                coupled_error = float(np.linalg.norm(coupled_centered - linear))
                feedback = float(np.linalg.norm(coupled_centered - frozen_centered))
                resolved_frozen, frozen_difference_norm, resolution_floor = centered_resolution(
                    frozen_plus_local,
                    frozen_minus_local,
                    base_local,
                    amplitude,
                    linear_norm,
                )
                resolved_coupled, coupled_difference_norm, _ = centered_resolution(
                    coupled_plus_local,
                    coupled_minus_local,
                    base_local,
                    amplitude,
                    linear_norm,
                )
                resolved = bool(resolved_frozen and resolved_coupled)

                R_plus = cached["coupled_plus"]["R_matrix"][edges][k3_edges]
                R_minus = cached["coupled_minus"]["R_matrix"][edges][k3_edges]
                centered_R = (R_plus - R_minus) / (2.0 * amplitude)
                centered_theta = wrapped_phase_centered(
                    perturbation["coupled_plus"].theta,
                    perturbation["coupled_minus"].theta,
                    amplitude,
                )
                centered_coherence = (
                    perturbation["coupled_plus"].coherence_acc
                    - perturbation["coupled_minus"].coherence_acc
                ) / (2.0 * amplitude)

                comparison_rows.append(
                    {
                        "step": step,
                        "time": step * dt,
                        "direction_id": perturbation["direction_id"],
                        "amplitude_fraction": perturbation["amplitude_fraction"],
                        "amplitude": amplitude,
                        "maximum_symmetric_amplitude": perturbation[
                            "maximum_symmetric_amplitude"
                        ],
                        "frozen_branch_preserved": cached["frozen_preserved"],
                        "coupled_branch_preserved": cached["coupled_preserved"],
                        "frozen_chi": cached["frozen_chi"],
                        "coupled_chi": cached["coupled_chi"],
                        "certified_branch_radius": radius,
                        "linear_norm": linear_norm,
                        "frozen_centered_norm": float(np.linalg.norm(frozen_centered)),
                        "coupled_centered_norm": float(np.linalg.norm(coupled_centered)),
                        "frozen_linear_absolute_error": frozen_error,
                        "coupled_linear_absolute_error": coupled_error,
                        "frozen_linear_relative_error": frozen_error
                        / max(linear_norm, ZERO_TOL),
                        "coupled_linear_relative_error": coupled_error
                        / max(linear_norm, ZERO_TOL),
                        "feedback_absolute_norm": feedback,
                        "feedback_fraction": feedback
                        / max(np.linalg.norm(coupled_centered), ZERO_TOL),
                        "centered_R_norm": float(np.linalg.norm(centered_R)),
                        "centered_theta_norm": float(np.linalg.norm(centered_theta)),
                        "centered_coherence_norm": float(
                            np.linalg.norm(centered_coherence)
                        ),
                        "frozen_difference_norm": frozen_difference_norm,
                        "coupled_difference_norm": coupled_difference_norm,
                        "resolution_floor": resolution_floor,
                        "numerically_resolved": resolved,
                    }
                )

        if step == future_steps:
            break

        # Advance frozen perturbations with exogenous base R_n.
        for perturbation, cached in zip(perturbations, branch_cache):
            perturbation["frozen_plus_B"] = cached["frozen_plus"]["projected"]
            perturbation["frozen_minus_B"] = cached["frozen_minus"]["projected"]
            perturbation["linear_vector"] = matrices[step] @ perturbation[
                "linear_vector"
            ]

            # Advance the complete perturbed states with their own R, phase,
            # EMA, and delayed histories.
            base.actual_step(
                perturbation["coupled_plus"],
                model,
                capacities,
                A,
                edges,
                args.boundary_tol,
                audit_operator=False,
            )
            base.actual_step(
                perturbation["coupled_minus"],
                model,
                capacities,
                A,
                edges,
                args.boundary_tol,
                audit_operator=False,
            )

        base.actual_step(
            state,
            model,
            capacities,
            A,
            edges,
            args.boundary_tol,
            audit_operator=False,
        )

    final_replay_exact = bool(np.array_equal(state.B, expected_final))
    final_replay_max_error = float(np.max(np.abs(state.B - expected_final)))
    coupled_frame = pd.DataFrame(comparison_rows)

    summary_rows: list[dict[str, Any]] = []
    for perturbation in perturbations:
        group = coupled_frame.loc[
            (coupled_frame["direction_id"] == perturbation["direction_id"])
            & (
                coupled_frame["amplitude_fraction"]
                == perturbation["amplitude_fraction"]
            )
        ]
        reliable = group.loc[group["numerically_resolved"]]
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
                "all_frozen_branch_preserved": perturbation[
                    "all_frozen_branch_preserved"
                ],
                "all_coupled_branch_preserved": perturbation[
                    "all_coupled_branch_preserved"
                ],
                "maximum_frozen_chi": perturbation["maximum_frozen_chi"],
                "maximum_coupled_chi": perturbation["maximum_coupled_chi"],
                "resolved_sample_count": int(len(reliable)),
                "last_resolved_time": float(reliable.iloc[-1]["time"])
                if len(reliable)
                else np.nan,
                "median_frozen_linear_error": float(
                    reliable["frozen_linear_relative_error"].median()
                )
                if len(reliable)
                else np.nan,
                "median_coupled_linear_error": float(
                    reliable["coupled_linear_relative_error"].median()
                )
                if len(reliable)
                else np.nan,
                "median_feedback_fraction": float(
                    reliable["feedback_fraction"].median()
                )
                if len(reliable)
                else np.nan,
                "maximum_feedback_fraction": float(
                    reliable["feedback_fraction"].max()
                )
                if len(reliable)
                else np.nan,
                "median_centered_R_norm": float(
                    reliable["centered_R_norm"].median()
                )
                if len(reliable)
                else np.nan,
                "median_centered_theta_norm": float(
                    reliable["centered_theta_norm"].median()
                )
                if len(reliable)
                else np.nan,
            }
        )
    coupled_summary = pd.DataFrame(summary_rows)

    component_audit.atomic_write_csv(
        output_dir / "stable_cocycle_spectra.csv", stable_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "dense_sliding_window_amplification.csv", window_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "coupled_frozen_centered_comparison.csv", coupled_frame
    )
    component_audit.atomic_write_csv(
        output_dir / "coupled_frozen_centered_summary.csv", coupled_summary
    )
    component_audit.atomic_savez(
        output_dir / "cocycle_control_matrices.npz",
        {
            "actual_time_varying": matrices,
            "K0": matrices[0],
            "Klate": matrices[-1],
            "diagonal_scale_only": diagonal_matrices,
            "directions": directions,
            "K3_nodes": k3_nodes,
            "K3_edges": k3_edges,
        },
    )

    report = make_report(
        stable_frame,
        window_frame,
        coupled_frame,
        coupled_summary,
        seed=args.seed,
        matrix_recompute_error=matrix_recompute_error,
        final_replay_exact=final_replay_exact,
        final_replay_max_error=final_replay_max_error,
    )
    component_audit.atomic_write_text(
        output_dir / "cocycle_controls_coupled_report.txt", report
    )

    source_path = Path(__file__).resolve()
    dependencies = {
        "stationarity": Path(base.__file__).resolve(),
        "component_audit": Path(component_audit.__file__).resolve(),
        "branch_audit": Path(branch_audit.__file__).resolve(),
        "frozen_cocycle": Path(frozen.__file__).resolve(),
    }
    analysis_manifest = {
        "analysis": "AIEF-1.4 stable cocycle controls and coupled-vs-frozen comparison",
        "source": {"path": str(source_path), "sha256": file_sha256(source_path)},
        "dependencies": {
            name: {"path": str(path), "sha256": file_sha256(path)}
            for name, path in dependencies.items()
        },
        "command": sys.argv,
        "inputs": {
            "npz": {"path": str(Path(args.npz).resolve()), "sha256": file_sha256(args.npz)},
            "manifest": {"path": str(Path(args.manifest).resolve()), "sha256": file_sha256(args.manifest)},
            "cocycle_npz": {"path": str(Path(args.cocycle_npz).resolve()), "sha256": file_sha256(args.cocycle_npz)},
            "cocycle_step": {"path": str(Path(args.cocycle_step).resolve()), "sha256": file_sha256(args.cocycle_step)},
        },
        "seed": args.seed,
        "K3_nodes": k3_nodes.tolist(),
        "K3_edges": k3_edges.tolist(),
        "dt": dt,
        "future_steps": future_steps,
        "scale_epsilon": args.scale_epsilon,
        "boundary_tolerance": args.boundary_tol,
        "sample_stride": args.sample_stride,
        "amplitude_fractions": args.amplitude_fractions,
        "dense_window_times": args.dense_window_times,
        "dense_window_start_stride": args.dense_window_start_stride,
        "matrix_recompute_max_error": matrix_recompute_error,
        "final_replay_exact": final_replay_exact,
        "final_replay_max_error": final_replay_max_error,
        "outputs": [
            "stable_cocycle_spectra.csv",
            "dense_sliding_window_amplification.csv",
            "coupled_frozen_centered_comparison.csv",
            "coupled_frozen_centered_summary.csv",
            "cocycle_control_matrices.npz",
            "cocycle_controls_coupled_report.txt",
        ],
        "interpretation_constraints": [
            "Stable finite-time exponents are not asserted asymptotic Oseledets exponents.",
            "Constant and diagonal-only cocycles are controlled counterfactuals, not additive causal decompositions.",
            "The coupled comparison is a centered nonlinear feedback diagnostic, not yet an analytic augmented Jacobian.",
            "Branch preservation and chi are checked dynamically for every perturbation.",
            "This is a deterministic analysis of one frozen seed, not independent population evidence.",
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
