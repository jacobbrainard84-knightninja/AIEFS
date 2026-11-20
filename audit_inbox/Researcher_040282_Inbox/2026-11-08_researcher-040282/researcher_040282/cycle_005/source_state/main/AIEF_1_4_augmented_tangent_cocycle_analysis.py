#!/usr/bin/env python3
"""Augmented directional tangent cocycle for the exceptional AIEF-1.4 replay.

This Stage-B analysis differentiates the complete implemented one-step state:

    X_n = (theta_n, B_n, coherence_acc_n, history_n).

It includes:
* phase and delayed-history sensitivity in dphi;
* the complex EMA update;
* the derivative of R=|C| followed by code-identical symmetrization;
* driver feedback dF=(eta+mu)dR-gamma*dB;
* positivity and the actual safeguarded admissibility map;
* phase coupling through the newly projected B;
* exact delay-history shifting.

Because endpoint minima can tie, the ambient admissibility map is generally
only directionally differentiable.  For each initial K3 direction the script
therefore propagates both +h and -h directional tangents.  Its prediction for
a centered nonlinear difference is

    (D Psi(X; h) - D Psi(X; -h)) / 2.

The analytic augmented tangent is compared against fully coupled centered
nonlinear replays over several feasible amplitudes.  Branch preservation, chi,
amplitude collapse on a common resolved horizon, and separate weight-driver
input norms are reported.

This is a deterministic one-seed mechanism analysis, not an independent
experiment and not yet a general theorem across AIEF trajectories.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
DEFAULT_OUTPUT_DIR = "aief_1_4_augmented_tangent_cocycle"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_BOUNDARY_TOL = 1e-9
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_SAMPLE_STRIDE = 10
DEFAULT_AMPLITUDE_FRACTIONS = "1e-3,1e-2,1e-1"
DEFAULT_MAGNITUDE_TOL = 1e-14
ZERO_TOL = 1e-14


@dataclass
class TangentState:
    theta: np.ndarray
    B: np.ndarray
    coherence_acc: np.ndarray
    history: deque[np.ndarray]

    def clone(self) -> "TangentState":
        return TangentState(
            theta=self.theta.copy(),
            B=self.B.copy(),
            coherence_acc=self.coherence_acc.copy(),
            history=deque(
                (item.copy() for item in self.history),
                maxlen=self.history.maxlen,
            ),
        )


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


def zero_tangent_like(state: base.DynamicState) -> TangentState:
    return TangentState(
        theta=np.zeros_like(state.theta, dtype=float),
        B=np.zeros_like(state.B, dtype=float),
        coherence_acc=np.zeros_like(state.coherence_acc, dtype=complex),
        history=deque(
            (np.zeros_like(item, dtype=float) for item in state.history),
            maxlen=state.history.maxlen,
        ),
    )


def base_intermediates(
    state: base.DynamicState,
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    scale_epsilon: float,
) -> dict[str, Any]:
    """Code-identical base intermediates for one actual step."""
    omega = np.asarray(model["omega"], dtype=float)
    dt = float(model["dt"])
    tau = float(model["tau"])
    t_window = float(model["T_window"])
    eta = float(model["eta"])
    mu = float(model["mu"])
    gamma = float(model["gamma"])

    delayed = state.history[0]
    dphi = (
        state.theta[:, None]
        - delayed[None, :]
        - ((omega[:, None] + omega[None, :]) / 2.0) * tau
    )
    ema_alpha = float(np.exp(-dt / t_window))
    phase_factor = np.exp(1j * dphi)
    updated_coherence = (
        ema_alpha * state.coherence_acc
        + (1.0 - ema_alpha) * phase_factor
    )
    R_raw = np.abs(updated_coherence)
    R = 0.5 * (R_raw + R_raw.T)
    np.fill_diagonal(R, 0.0)

    F_matrix = (eta + mu) * R - mu - gamma * state.B
    F_matrix = 0.5 * (F_matrix + F_matrix.T)
    np.fill_diagonal(F_matrix, 0.0)

    z = state.B + dt * F_matrix
    proposal = np.maximum(z, 0.0)
    proposal = 0.5 * (proposal + proposal.T)
    np.fill_diagonal(proposal, 0.0)
    x = proposal[edges]
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

    phase_argument = delayed[None, :] - state.theta[:, None]
    sine = np.sin(phase_argument)
    cosine = np.cos(phase_argument)
    coupling = np.sum(projected * sine, axis=1)
    theta_unwrapped = state.theta + dt * (omega + coupling)
    theta_new = np.mod(theta_unwrapped, 2.0 * np.pi)

    return {
        "omega": omega,
        "dt": dt,
        "ema_alpha": ema_alpha,
        "delayed": delayed,
        "dphi": dphi,
        "phase_factor": phase_factor,
        "updated_coherence": updated_coherence,
        "R_raw": R_raw,
        "R": R,
        "F_matrix": F_matrix,
        "z": z,
        "proposal": proposal,
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
        "phase_argument": phase_argument,
        "sine": sine,
        "cosine": cosine,
        "coupling": coupling,
        "theta_unwrapped": theta_unwrapped,
        "theta_new": theta_new,
        "scale_epsilon": scale_epsilon,
    }


def positivity_directional_derivative(
    z: np.ndarray,
    dz: np.ndarray,
    tie_tolerance: float = 0.0,
) -> tuple[np.ndarray, int]:
    result = np.zeros_like(dz, dtype=float)
    positive = z > tie_tolerance
    negative = z < -tie_tolerance
    boundary = ~(positive | negative)
    result[positive] = dz[positive]
    result[negative] = 0.0
    result[boundary] = np.maximum(dz[boundary], 0.0)
    return result, int(np.sum(boundary))


def admissibility_directional_matrix(
    intermediate: dict[str, Any],
    dproposal: np.ndarray,
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
) -> tuple[np.ndarray, dict[str, Any]]:
    """Directional derivative of the executed safeguarded scaling stage."""
    dproposal = 0.5 * (dproposal + dproposal.T)
    np.fill_diagonal(dproposal, 0.0)
    dx = dproposal[edges]
    if not intermediate["gate_on"]:
        return dproposal.copy(), {
            "node_scale_derivative": np.zeros(len(capacities)),
            "active_tie_count": 0,
        }

    q = intermediate["q_scale"]
    scales = intermediate["scales"]
    eps = float(intermediate["scale_epsilon"])
    dq = np.sum(dproposal, axis=1)
    ds = np.zeros(len(capacities), dtype=float)
    clip_margin = q + eps - capacities
    for node in range(len(capacities)):
        if clip_margin[node] > 0.0:
            ds[node] = -scales[node] / (q[node] + eps) * dq[node]
        elif clip_margin[node] < 0.0:
            ds[node] = 0.0
        else:
            ds[node] = min(0.0, -dq[node] / capacities[node])

    dy = np.empty(len(dx), dtype=float)
    active_ties = 0
    x = intermediate["x"]
    for edge, (i_raw, j_raw) in enumerate(zip(edges[0], edges[1])):
        i = int(i_raw)
        j = int(j_raw)
        if scales[i] < scales[j]:
            dm = ds[i]
        elif scales[j] < scales[i]:
            dm = ds[j]
        else:
            dm = min(ds[i], ds[j])
            if scales[i] < 1.0:
                active_ties += 1
        multiplier = min(scales[i], scales[j])
        dy[edge] = multiplier * dx[edge] + x[edge] * dm
    return base.vector_to_matrix(dy, dproposal.shape[0], edges), {
        "node_scale_derivative": ds,
        "active_tie_count": active_ties,
    }


def tangent_step(
    tangent: TangentState,
    intermediate: dict[str, Any],
    model: dict[str, Any],
    capacities: np.ndarray,
    A: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    magnitude_tolerance: float,
    *,
    ablation: dict[str, bool] | None = None,
) -> tuple[TangentState, dict[str, Any]]:
    """One directional tangent step along the already computed base step.

    Optional ablations are counterfactual tangent transfers evaluated along
    the unchanged base replay.  Supported boolean keys are:
    use_current_phase, use_delayed_history, use_ema_memory,
    use_fresh_phase, and use_R_to_weight.  Omitted keys default to True.
    """
    config = {
        "use_current_phase": True,
        "use_delayed_history": True,
        "use_ema_memory": True,
        "use_fresh_phase": True,
        "use_R_to_weight": True,
    }
    if ablation is not None:
        unknown = set(ablation) - set(config)
        if unknown:
            raise ValueError(f"unknown tangent ablation keys: {sorted(unknown)}")
        config.update(ablation)

    eta = float(model["eta"])
    mu = float(model["mu"])
    gamma = float(model["gamma"])
    dt = float(model["dt"])

    ddelayed = tangent.history[0]
    ddphi = np.zeros_like(intermediate["dphi"], dtype=float)
    if config["use_current_phase"]:
        ddphi += tangent.theta[:, None]
    if config["use_delayed_history"]:
        ddphi -= ddelayed[None, :]
    dcoherence_new = np.zeros_like(tangent.coherence_acc, dtype=complex)
    if config["use_ema_memory"]:
        dcoherence_new += intermediate["ema_alpha"] * tangent.coherence_acc
    if config["use_fresh_phase"]:
        dcoherence_new += (
            (1.0 - intermediate["ema_alpha"])
            * 1j
            * intermediate["phase_factor"]
            * ddphi
        )

    magnitude = intermediate["R_raw"]
    dR_raw = np.empty_like(magnitude, dtype=float)
    regular = magnitude > magnitude_tolerance
    dR_raw[regular] = np.real(
        np.conj(intermediate["updated_coherence"][regular])
        * dcoherence_new[regular]
    ) / magnitude[regular]
    dR_raw[~regular] = np.abs(dcoherence_new[~regular])
    dR = 0.5 * (dR_raw + dR_raw.T)
    np.fill_diagonal(dR, 0.0)

    driver_dR = dR if config["use_R_to_weight"] else np.zeros_like(dR)
    dF = (eta + mu) * driver_dR - gamma * tangent.B
    dF = 0.5 * (dF + dF.T)
    np.fill_diagonal(dF, 0.0)
    dz_weight = (1.0 - gamma * dt) * tangent.B
    dz_driver = dt * (eta + mu) * driver_dR
    dz = tangent.B + dt * dF

    dproposal_raw, positivity_ties = positivity_directional_derivative(
        intermediate["z"], dz
    )
    dproposal = 0.5 * (dproposal_raw + dproposal_raw.T)
    np.fill_diagonal(dproposal, 0.0)
    dB_new, admissibility_info = admissibility_directional_matrix(
        intermediate, dproposal, capacities, A, edges
    )

    # Controlled directional decompositions.  At endpoint ties the derivative
    # is positively homogeneous but not additive, so an interaction residual
    # is explicitly retained.
    dproposal_weight_raw, _ = positivity_directional_derivative(
        intermediate["z"], dz_weight
    )
    dproposal_driver_raw, _ = positivity_directional_derivative(
        intermediate["z"], dz_driver
    )
    dproposal_weight = 0.5 * (
        dproposal_weight_raw + dproposal_weight_raw.T
    )
    dproposal_driver = 0.5 * (
        dproposal_driver_raw + dproposal_driver_raw.T
    )
    np.fill_diagonal(dproposal_weight, 0.0)
    np.fill_diagonal(dproposal_driver, 0.0)
    dB_weight, _ = admissibility_directional_matrix(
        intermediate, dproposal_weight, capacities, A, edges
    )
    dB_driver, _ = admissibility_directional_matrix(
        intermediate, dproposal_driver, capacities, A, edges
    )
    dB_interaction = dB_new - dB_weight - dB_driver

    dphase_argument = ddelayed[None, :] - tangent.theta[:, None]
    dcoupling = np.sum(
        dB_new * intermediate["sine"]
        + intermediate["projected"]
        * intermediate["cosine"]
        * dphase_argument,
        axis=1,
    )
    dtheta_new = tangent.theta + dt * dcoupling

    history_new = deque(
        (item.copy() for item in tangent.history),
        maxlen=tangent.history.maxlen,
    )
    history_new.append(dtheta_new.copy())
    new_tangent = TangentState(
        theta=dtheta_new,
        B=dB_new,
        coherence_acc=dcoherence_new,
        history=history_new,
    )
    return new_tangent, {
        "dR": dR,
        "dF": dF,
        "dB_weight": dB_weight,
        "dB_driver": dB_driver,
        "dB_interaction": dB_interaction,
        "positivity_tie_count": positivity_ties,
        "magnitude_zero_count": int(np.sum(~regular)),
        "active_endpoint_tie_count": admissibility_info["active_tie_count"],
        "ablation_config": config.copy(),
    }


def advance_base_state(
    state: base.DynamicState,
    intermediate: dict[str, Any],
) -> None:
    state.B = intermediate["projected"].copy()
    state.coherence_acc = intermediate["updated_coherence"].copy()
    state.theta = intermediate["theta_new"].copy()
    state.history.append(state.theta.copy())


def wrapped_difference(
    plus: np.ndarray,
    minus: np.ndarray,
    denominator: float,
) -> np.ndarray:
    return np.angle(np.exp(1j * (plus - minus))) / denominator


def tangent_centered(
    plus: TangentState,
    minus: TangentState,
) -> TangentState:
    return TangentState(
        theta=0.5 * (plus.theta - minus.theta),
        B=0.5 * (plus.B - minus.B),
        coherence_acc=0.5 * (
            plus.coherence_acc - minus.coherence_acc
        ),
        history=deque(
            (
                0.5 * (plus_item - minus_item)
                for plus_item, minus_item in zip(plus.history, minus.history)
            ),
            maxlen=plus.history.maxlen,
        ),
    )


def tangent_history_array(tangent: TangentState) -> np.ndarray:
    return np.asarray(list(tangent.history), dtype=float)


def nonlinear_history_centered(
    plus: base.DynamicState,
    minus: base.DynamicState,
    amplitude: float,
) -> np.ndarray:
    plus_history = np.asarray(list(plus.history), dtype=float)
    minus_history = np.asarray(list(minus.history), dtype=float)
    return wrapped_difference(
        plus_history, minus_history, 2.0 * amplitude
    )


def resolution_status(
    plus: np.ndarray,
    minus: np.ndarray,
    base_value: np.ndarray,
    amplitude: float,
    predicted_norm: float,
) -> tuple[bool, float]:
    difference_norm = float(np.linalg.norm(plus - minus))
    floor = float(
        100.0
        * np.finfo(float).eps
        * max(np.linalg.norm(base_value), 1.0)
    )
    return bool(
        difference_norm > floor
        and 2.0 * amplitude * predicted_norm > floor
    ), floor


def make_report(
    comparison: pd.DataFrame,
    summary: pd.DataFrame,
    collapse: pd.DataFrame,
    *,
    seed: str,
    final_replay_exact: bool,
    final_replay_max_error: float,
    base_step_reproduction_error: float,
) -> str:
    lines = [
        "AIEF exceptional K3 augmented tangent cocycle analysis",
        "======================================================",
        "",
        "Identity and scope",
        "------------------",
        f"Seed: {seed}",
        f"Final base replay exact: {final_replay_exact}",
        f"Final base replay maximum error: {final_replay_max_error:.6g}",
        f"Maximum custom-step versus implemented-step error: {base_step_reproduction_error:.6g}",
        "* Analytic tangents include phase, delay history, complex EMA, R feedback, admissibility, and phase coupling.",
        "",
        "Augmented tangent versus coupled centered replay",
        "------------------------------------------------",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"  direction={int(row['direction_id'])}, fraction={row['amplitude_fraction']:.3g}, "
            f"amplitude={row['amplitude']:.3g}, branch={bool(row['all_branch_preserved'])}, "
            f"max_chi={row['maximum_chi']:.3g}, resolved={int(row['resolved_sample_count'])}, "
            f"last_time={row['last_resolved_time']:.3g}, "
            f"median_K3_error={row['median_K3_relative_error']:.3g}, "
            f"median_full_B_error={row['median_full_B_relative_error']:.3g}, "
            f"median_theta_error={row['median_theta_relative_error']:.3g}, "
            f"median_R_error={row['median_R_relative_error']:.3g}"
        )

    reliable = comparison.loc[comparison["numerically_resolved"]]
    if len(reliable):
        lines.extend(
            [
                "",
                f"Overall median K3 augmented error: {reliable['K3_relative_error'].median():.6g}",
                f"Overall maximum K3 augmented error: {reliable['K3_relative_error'].max():.6g}",
                f"Overall median full-B augmented error: {reliable['full_B_relative_error'].median():.6g}",
                f"Overall median phase augmented error: {reliable['theta_relative_error'].median():.6g}",
                f"Overall median R augmented error: {reliable['R_relative_error'].median():.6g}",
                f"Median analytic driver/weight output ratio: {reliable['driver_to_weight_output_ratio'].median():.6g}",
                f"Maximum analytic nonadditive tie interaction ratio: {reliable['interaction_to_full_output_ratio'].max():.6g}",
            ]
        )

    lines.extend(["", "Matched-horizon amplitude collapse", "----------------------------------"])
    for _, row in collapse.iterrows():
        lines.append(
            f"  direction={int(row['direction_id'])}: common_last_time={row['common_last_time']:.6g}, "
            f"common_samples={int(row['common_sample_count'])}, "
            f"median_vector_spread={row['median_centered_vector_spread']:.6g}, "
            f"maximum_vector_spread={row['maximum_centered_vector_spread']:.6g}, "
            f"median_augmented_error={row['median_augmented_error_common']:.6g}"
        )

    lines.extend(
        [
            "",
            "Interpretation constraints",
            "--------------------------",
            "* The map is directionally differentiated at endpoint and positivity ties; +h and -h tangents are propagated separately.",
            "* Centered analytic predictions use (D(+h)-D(-h))/2 and need not equal either one-sided tangent.",
            "* Amplitude collapse is evaluated only on the common numerically resolved horizon.",
            "* A safeguard-dominated normal mode remains part of the implemented discrete dynamics even if absent from an intended continuum limit.",
            "* Agreement is established for this seed, directions, amplitudes, and horizon only.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--cocycle-npz", default=DEFAULT_COCYCLE_NPZ)
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
        "--magnitude-tol", type=float, default=DEFAULT_MAGNITUDE_TOL
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    for path in (args.npz, args.manifest, args.cocycle_npz):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    if min(
        args.boundary_tol,
        args.scale_epsilon,
        args.magnitude_tol,
    ) <= 0.0:
        raise ValueError("tolerances and epsilon must be positive")
    if args.sample_stride <= 0:
        raise ValueError("sample-stride must be positive")
    if args.scale_epsilon != DEFAULT_SCALE_EPSILON:
        raise ValueError(
            "the implemented actual_step hard-codes scale epsilon=1e-12; "
            "a different epsilon requires a separately versioned dynamics map"
        )

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
    future_steps = int(manifest["protocol"]["future_steps"])

    with np.load(args.cocycle_npz, allow_pickle=False) as data:
        matrices = np.asarray(data["K3_matrix_sequence"], dtype=float).copy()
        directions = np.asarray(data["K3_direction_basis"], dtype=float).copy()
        k3_nodes = np.asarray(data["K3_nodes"], dtype=int).copy()
        k3_edges = np.asarray(data["K3_edges"], dtype=int).copy()
    if matrices.shape != (future_steps, 3, 3):
        raise ValueError(f"unexpected cocycle matrix shape {matrices.shape}")

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

        tangent_plus = zero_tangent_like(split_state)
        tangent_minus = zero_tangent_like(split_state)
        tangent_plus.B = base.vector_to_matrix(
            full_direction, node_count, edges
        )
        tangent_minus.B = -tangent_plus.B.copy()

        perturbations.append(
            {
                "direction_id": direction_id,
                "direction": local_direction.copy(),
                "full_direction": full_direction,
                "maximum_symmetric_amplitude": maximum,
                "tangent_plus": tangent_plus,
                "tangent_minus": tangent_minus,
                "linear_frozen": local_direction.copy(),
                "amplitudes": [],
            }
        )
        for fraction in args.amplitude_fractions:
            amplitude = fraction * maximum
            if not np.isfinite(amplitude) or amplitude <= 1e-14:
                continue
            plus_w = split_w + amplitude * full_direction
            minus_w = split_w - amplitude * full_direction
            coupled_plus = split_state.clone()
            coupled_minus = split_state.clone()
            coupled_plus.B = base.vector_to_matrix(
                plus_w, node_count, edges
            )
            coupled_minus.B = base.vector_to_matrix(
                minus_w, node_count, edges
            )
            perturbations[-1]["amplitudes"].append(
                {
                    "amplitude_fraction": fraction,
                    "amplitude": amplitude,
                    "plus": coupled_plus,
                    "minus": coupled_minus,
                    "all_branch_preserved": True,
                    "maximum_chi": 0.0,
                }
            )

    state = split_state.clone()
    comparison_rows: list[dict[str, Any]] = []
    base_step_reproduction_error = 0.0

    for step in range(future_steps + 1):
        intermediate = base_intermediates(
            state,
            model,
            capacities,
            A,
            edges,
            args.scale_epsilon,
        )
        base_signature = json_compact(
            {
                "gate": int(intermediate["gate_on"]),
                "winners": intermediate["winner_code"][k3_edges].tolist(),
            }
        )
        radius, _ = branch_audit.certified_subspace_branch_radius(
            intermediate["x"],
            capacities,
            A,
            edges,
            k3_edges,
            args.scale_epsilon,
        )

        tangent_next: list[tuple[TangentState, TangentState, dict[str, Any], dict[str, Any]]] = []
        for perturbation in perturbations:
            next_plus, diag_plus = tangent_step(
                perturbation["tangent_plus"],
                intermediate,
                model,
                capacities,
                A,
                edges,
                args.magnitude_tol,
            )
            next_minus, diag_minus = tangent_step(
                perturbation["tangent_minus"],
                intermediate,
                model,
                capacities,
                A,
                edges,
                args.magnitude_tol,
            )
            tangent_next.append((next_plus, next_minus, diag_plus, diag_minus))

        branch_cache: list[list[dict[str, Any]]] = []
        for perturbation in perturbations:
            direction_cache: list[dict[str, Any]] = []
            for amplitude_case in perturbation["amplitudes"]:
                plus_branch = branch_audit.proposal_and_admissibility_branch(
                    amplitude_case["plus"],
                    model,
                    capacities,
                    A,
                    edges,
                    args.scale_epsilon,
                )
                minus_branch = branch_audit.proposal_and_admissibility_branch(
                    amplitude_case["minus"],
                    model,
                    capacities,
                    A,
                    edges,
                    args.scale_epsilon,
                )
                plus_signature = frozen.branch_signature(plus_branch, k3_edges)
                minus_signature = frozen.branch_signature(minus_branch, k3_edges)
                preserved = bool(
                    plus_signature == base_signature
                    and minus_signature == base_signature
                )
                amplitude_case["all_branch_preserved"] &= preserved
                proposal_delta = max(
                    np.linalg.norm(
                        plus_branch["x"][k3_edges]
                        - intermediate["x"][k3_edges]
                    ),
                    np.linalg.norm(
                        minus_branch["x"][k3_edges]
                        - intermediate["x"][k3_edges]
                    ),
                )
                chi = float(
                    proposal_delta / max(radius, np.finfo(float).tiny)
                )
                amplitude_case["maximum_chi"] = max(
                    amplitude_case["maximum_chi"], chi
                )
                direction_cache.append(
                    {
                        "plus_branch": plus_branch,
                        "minus_branch": minus_branch,
                        "preserved": preserved,
                        "chi": chi,
                    }
                )
            branch_cache.append(direction_cache)

        if step % args.sample_stride == 0 or step == future_steps:
            for direction_index, perturbation in enumerate(perturbations):
                tangent_center = tangent_centered(
                    perturbation["tangent_plus"],
                    perturbation["tangent_minus"],
                )
                _, _, diag_plus, diag_minus = tangent_next[direction_index]
                analytic_dR = 0.5 * (diag_plus["dR"] - diag_minus["dR"])
                analytic_weight_output = 0.5 * (
                    diag_plus["dB_weight"] - diag_minus["dB_weight"]
                )
                analytic_driver_output = 0.5 * (
                    diag_plus["dB_driver"] - diag_minus["dB_driver"]
                )
                analytic_interaction = 0.5 * (
                    diag_plus["dB_interaction"] - diag_minus["dB_interaction"]
                )
                analytic_full_B_edges = tangent_center.B[edges]
                analytic_K3 = analytic_full_B_edges[k3_edges]
                analytic_theta = tangent_center.theta
                analytic_C = tangent_center.coherence_acc
                analytic_history = tangent_history_array(tangent_center)

                for amplitude_case, cached in zip(
                    perturbation["amplitudes"], branch_cache[direction_index]
                ):
                    amplitude = amplitude_case["amplitude"]
                    plus = amplitude_case["plus"]
                    minus = amplitude_case["minus"]
                    nonlinear_B_edges = (
                        plus.B[edges] - minus.B[edges]
                    ) / (2.0 * amplitude)
                    nonlinear_K3 = nonlinear_B_edges[k3_edges]
                    nonlinear_theta = wrapped_difference(
                        plus.theta, minus.theta, 2.0 * amplitude
                    )
                    nonlinear_C = (
                        plus.coherence_acc - minus.coherence_acc
                    ) / (2.0 * amplitude)
                    nonlinear_history = nonlinear_history_centered(
                        plus, minus, amplitude
                    )
                    nonlinear_R = (
                        cached["plus_branch"]["R_matrix"]
                        - cached["minus_branch"]["R_matrix"]
                    ) / (2.0 * amplitude)

                    K3_error = float(
                        np.linalg.norm(nonlinear_K3 - analytic_K3)
                    )
                    full_B_error = float(
                        np.linalg.norm(nonlinear_B_edges - analytic_full_B_edges)
                    )
                    theta_error = float(
                        np.linalg.norm(nonlinear_theta - analytic_theta)
                    )
                    C_error = float(np.linalg.norm(nonlinear_C - analytic_C))
                    history_error = float(
                        np.linalg.norm(nonlinear_history - analytic_history)
                    )
                    R_error = float(np.linalg.norm(nonlinear_R - analytic_dR))
                    predicted_norm = float(np.linalg.norm(analytic_K3))
                    resolved, resolution_floor = resolution_status(
                        plus.B[edges][k3_edges],
                        minus.B[edges][k3_edges],
                        state.B[edges][k3_edges],
                        amplitude,
                        predicted_norm,
                    )

                    weight_norm = float(
                        np.linalg.norm(analytic_weight_output[edges][k3_edges])
                    )
                    driver_norm = float(
                        np.linalg.norm(analytic_driver_output[edges][k3_edges])
                    )
                    interaction_norm = float(
                        np.linalg.norm(analytic_interaction[edges][k3_edges])
                    )
                    full_output_norm = float(
                        np.linalg.norm(
                            0.5
                            * (
                                tangent_next[direction_index][0].B
                                - tangent_next[direction_index][1].B
                            )[edges][k3_edges]
                        )
                    )

                    comparison_rows.append(
                        {
                            "step": step,
                            "time": step * dt,
                            "direction_id": perturbation["direction_id"],
                            "amplitude_fraction": amplitude_case[
                                "amplitude_fraction"
                            ],
                            "amplitude": amplitude,
                            "branch_preserved": cached["preserved"],
                            "chi": cached["chi"],
                            "numerically_resolved": resolved,
                            "resolution_floor": resolution_floor,
                            "analytic_K3_norm": predicted_norm,
                            "nonlinear_K3_norm": float(
                                np.linalg.norm(nonlinear_K3)
                            ),
                            "K3_absolute_error": K3_error,
                            "K3_relative_error": K3_error
                            / max(predicted_norm, ZERO_TOL),
                            "full_B_relative_error": full_B_error
                            / max(np.linalg.norm(analytic_full_B_edges), ZERO_TOL),
                            "theta_relative_error": theta_error
                            / max(np.linalg.norm(analytic_theta), ZERO_TOL),
                            "coherence_relative_error": C_error
                            / max(np.linalg.norm(analytic_C), ZERO_TOL),
                            "history_relative_error": history_error
                            / max(np.linalg.norm(analytic_history), ZERO_TOL),
                            "R_relative_error": R_error
                            / max(np.linalg.norm(analytic_dR), ZERO_TOL),
                            "analytic_R_norm": float(np.linalg.norm(analytic_dR)),
                            "analytic_theta_norm": float(
                                np.linalg.norm(analytic_theta)
                            ),
                            "analytic_coherence_norm": float(
                                np.linalg.norm(analytic_C)
                            ),
                            "weight_output_norm": weight_norm,
                            "driver_output_norm": driver_norm,
                            "interaction_output_norm": interaction_norm,
                            "driver_to_weight_output_ratio": driver_norm
                            / max(weight_norm, ZERO_TOL),
                            "interaction_to_full_output_ratio": interaction_norm
                            / max(full_output_norm, ZERO_TOL),
                            "coupled_K3_vector_json": json_compact(
                                nonlinear_K3.tolist()
                            ),
                            "analytic_K3_vector_json": json_compact(
                                analytic_K3.tolist()
                            ),
                            "coupled_R_K3_vector_json": json_compact(
                                nonlinear_R[edges][k3_edges].tolist()
                            ),
                            "analytic_R_K3_vector_json": json_compact(
                                analytic_dR[edges][k3_edges].tolist()
                            ),
                        }
                    )

        if step == future_steps:
            break

        # Advance nonlinear coupled perturbations using the implemented step.
        for perturbation in perturbations:
            for amplitude_case in perturbation["amplitudes"]:
                base.actual_step(
                    amplitude_case["plus"],
                    model,
                    capacities,
                    A,
                    edges,
                    args.boundary_tol,
                    audit_operator=False,
                )
                base.actual_step(
                    amplitude_case["minus"],
                    model,
                    capacities,
                    A,
                    edges,
                    args.boundary_tol,
                    audit_operator=False,
                )

        # Advance analytic directional tangents.
        for perturbation, next_values in zip(perturbations, tangent_next):
            perturbation["tangent_plus"] = next_values[0]
            perturbation["tangent_minus"] = next_values[1]
            perturbation["linear_frozen"] = matrices[step] @ perturbation[
                "linear_frozen"
            ]

        # Verify the custom base step against the implemented step, then use
        # the custom result so all tangent intermediates share identical bases.
        reference = state.clone()
        base.actual_step(
            reference,
            model,
            capacities,
            A,
            edges,
            args.boundary_tol,
            audit_operator=False,
        )
        advance_base_state(state, intermediate)
        base_step_reproduction_error = max(
            base_step_reproduction_error,
            float(np.max(np.abs(reference.B - state.B))),
            float(np.max(np.abs(reference.theta - state.theta))),
            float(
                np.max(
                    np.abs(
                        reference.coherence_acc - state.coherence_acc
                    )
                )
            ),
            float(
                np.max(
                    np.abs(
                        np.asarray(list(reference.history))
                        - np.asarray(list(state.history))
                    )
                )
            ),
        )

    final_replay_exact = bool(np.array_equal(state.B, expected_final))
    final_replay_max_error = float(np.max(np.abs(state.B - expected_final)))
    comparison = pd.DataFrame(comparison_rows)

    summary_rows: list[dict[str, Any]] = []
    for perturbation in perturbations:
        for amplitude_case in perturbation["amplitudes"]:
            group = comparison.loc[
                (comparison["direction_id"] == perturbation["direction_id"])
                & (
                    comparison["amplitude_fraction"]
                    == amplitude_case["amplitude_fraction"]
                )
            ]
            reliable = group.loc[group["numerically_resolved"]]
            summary_rows.append(
                {
                    "direction_id": perturbation["direction_id"],
                    "amplitude_fraction": amplitude_case[
                        "amplitude_fraction"
                    ],
                    "amplitude": amplitude_case["amplitude"],
                    "all_branch_preserved": amplitude_case[
                        "all_branch_preserved"
                    ],
                    "maximum_chi": amplitude_case["maximum_chi"],
                    "resolved_sample_count": int(len(reliable)),
                    "last_resolved_time": float(reliable.iloc[-1]["time"])
                    if len(reliable)
                    else np.nan,
                    "median_K3_relative_error": float(
                        reliable["K3_relative_error"].median()
                    )
                    if len(reliable)
                    else np.nan,
                    "maximum_K3_relative_error": float(
                        reliable["K3_relative_error"].max()
                    )
                    if len(reliable)
                    else np.nan,
                    "median_full_B_relative_error": float(
                        reliable["full_B_relative_error"].median()
                    )
                    if len(reliable)
                    else np.nan,
                    "median_theta_relative_error": float(
                        reliable["theta_relative_error"].median()
                    )
                    if len(reliable)
                    else np.nan,
                    "median_R_relative_error": float(
                        reliable["R_relative_error"].median()
                    )
                    if len(reliable)
                    else np.nan,
                }
            )
    summary = pd.DataFrame(summary_rows)

    collapse_rows: list[dict[str, Any]] = []
    for direction_id, direction_group in comparison.groupby("direction_id"):
        resolved_last = (
            summary.loc[summary["direction_id"] == direction_id, "last_resolved_time"]
            .dropna()
            .to_numpy(float)
        )
        common_last = float(np.min(resolved_last)) if len(resolved_last) else np.nan
        common = direction_group.loc[
            direction_group["numerically_resolved"]
            & (direction_group["time"] <= common_last)
        ] if np.isfinite(common_last) else direction_group.iloc[0:0]
        spreads: list[float] = []
        analytic_errors: list[float] = []
        common_times = []
        for time, time_group in common.groupby("time"):
            if len(time_group) != len(args.amplitude_fractions):
                continue
            vectors = [
                np.asarray(json.loads(value), dtype=float)
                for value in time_group.sort_values("amplitude_fraction")[
                    "coupled_K3_vector_json"
                ]
            ]
            reference_vector = vectors[0]
            spread = max(
                np.linalg.norm(vector - reference_vector)
                / max(np.linalg.norm(reference_vector), ZERO_TOL)
                for vector in vectors[1:]
            ) if len(vectors) > 1 else 0.0
            spreads.append(float(spread))
            analytic_errors.extend(
                time_group["K3_relative_error"].to_numpy(float).tolist()
            )
            common_times.append(time)
        collapse_rows.append(
            {
                "direction_id": int(direction_id),
                "common_last_time": common_last,
                "common_sample_count": len(common_times),
                "median_centered_vector_spread": float(np.median(spreads))
                if spreads
                else np.nan,
                "maximum_centered_vector_spread": float(np.max(spreads))
                if spreads
                else np.nan,
                "median_augmented_error_common": float(
                    np.median(analytic_errors)
                )
                if analytic_errors
                else np.nan,
            }
        )
    collapse = pd.DataFrame(collapse_rows)

    component_audit.atomic_write_csv(
        output_dir / "augmented_tangent_comparison.csv", comparison
    )
    component_audit.atomic_write_csv(
        output_dir / "augmented_tangent_summary.csv", summary
    )
    component_audit.atomic_write_csv(
        output_dir / "matched_horizon_amplitude_collapse.csv", collapse
    )

    report = make_report(
        comparison,
        summary,
        collapse,
        seed=args.seed,
        final_replay_exact=final_replay_exact,
        final_replay_max_error=final_replay_max_error,
        base_step_reproduction_error=base_step_reproduction_error,
    )
    component_audit.atomic_write_text(
        output_dir / "augmented_tangent_report.txt", report
    )

    source_path = Path(__file__).resolve()
    dependencies = {
        "stationarity": Path(base.__file__).resolve(),
        "component_audit": Path(component_audit.__file__).resolve(),
        "branch_audit": Path(branch_audit.__file__).resolve(),
        "frozen_cocycle": Path(frozen.__file__).resolve(),
    }
    analysis_manifest = {
        "analysis": "AIEF-1.4 augmented directional tangent cocycle",
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
        },
        "seed": args.seed,
        "K3_nodes": k3_nodes.tolist(),
        "K3_edges": k3_edges.tolist(),
        "dt": dt,
        "future_steps": future_steps,
        "scale_epsilon": args.scale_epsilon,
        "boundary_tolerance": args.boundary_tol,
        "magnitude_tolerance": args.magnitude_tol,
        "sample_stride": args.sample_stride,
        "amplitude_fractions": args.amplitude_fractions,
        "final_replay_exact": final_replay_exact,
        "final_replay_max_error": final_replay_max_error,
        "base_step_reproduction_max_error": base_step_reproduction_error,
        "outputs": [
            "augmented_tangent_comparison.csv",
            "augmented_tangent_summary.csv",
            "matched_horizon_amplitude_collapse.csv",
            "augmented_tangent_report.txt",
        ],
        "interpretation_constraints": [
            "The augmented map is directionally differentiated at ties; +h and -h tangents are propagated separately.",
            "Centered predictions use the odd part of the directional derivative.",
            "Amplitude collapse is assessed only on a common numerically resolved horizon.",
            "Agreement is conditional on the audited branch and tested directions.",
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
