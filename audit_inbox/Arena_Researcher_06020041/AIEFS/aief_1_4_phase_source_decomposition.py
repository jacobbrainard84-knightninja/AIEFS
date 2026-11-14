#!/usr/bin/env python3

"""
AIEF-1.4 Phase-Increment Source Decomposition (Diagnostic Script)

Illuminates the upstream open problem:
  Why does the source increment S_n = Delta z_{n+1} - Delta z_n decay at the EMA rate?

The directed phase increment decomposes exactly (Proposition 3.1, operator/cocycle note):
  Delta phi_{ij,n} = dt * omega_i + dt * G_{i,n} - Delta h_{j,n}

where:
  G_{i,n} = sum_k B_{ik,n+1} * sin(h_{k,n} - theta_{i,n})   [projected coupling]
  Delta h_{j,n} = h_{j,n+1} - h_{j,n}                        [history change]

For an edge difference (a vs b), the source increment S_n is driven by:
  1. Intrinsic frequency difference:  dt * (omega_{ia} - omega_{ib})
  2. Coupling difference:             dt * (G_{ia,n} - G_{ib,n})
  3. History difference:              -(Delta h_{ja,n} - Delta h_{jb,n})

This script:
- Loads the frozen production replay
- Decomposes S_n into these three components for both channels
- Fits decay rates for each component independently
- Shows cancellation structure and rate inheritance

This is mechanism illumination, not a proof.
The upstream theorem (deriving alpha-rate alignment from phase dynamics) remains open.

Evidence class: diagnostic mechanism exploration
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# === Constants ===
DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_phase_source_decomposition"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_SIGNAL_FLOOR = 1e-14
DEFAULT_INTERVALS = "0,50,100,150,200,250,300,320"

# K3 edge pairs for the two channels (directed)
CHANNEL_EDGES = {
    "fixed_left": {
        "edge_a": (2, 7), "edge_b": (7, 11),
        "rev_a": (7, 2), "rev_b": (11, 7),
    },
    "right_mode": {
        "edge_a": (7, 11), "edge_b": (2, 11),
        "rev_a": (11, 7), "rev_b": (11, 2),
    },
}


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def compute_module_sha256(module):
    if module is None or not hasattr(module, "__file__") or module.__file__ is None:
        return "not_available"
    return file_sha256(Path(module.__file__).resolve())


def load_production_modules():
    import AIEF_1_4_stationarity_perturbation_analysis_updated as base
    import AIEF_1_4_component_controller_audit as component_audit
    import AIEF_1_4_augmented_tangent_cocycle_analysis as augmented
    return base, component_audit, augmented


def safe_atomic_write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def safe_atomic_write_csv(path, df):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            df.to_csv(f, index=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def parse_nonnegative_float_list(value):
    try:
        values = [float(x.strip()) for x in value.split(",") if x.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated floats") from exc
    if not values or any(v < 0.0 for v in values):
        raise argparse.ArgumentTypeError("values must be nonnegative")
    return sorted(set(values))


def fit_log_rate(times, values, floor):
    magnitudes = np.abs(np.asarray(values, dtype=float))
    valid = np.isfinite(magnitudes) & (magnitudes > floor)
    if np.sum(valid) < 3:
        return {"rate": np.nan, "R_squared": np.nan, "count": int(np.sum(valid))}
    x = np.asarray(times, dtype=float)[valid]
    y = np.log(magnitudes[valid])
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "rate": float(-slope),
        "R_squared": float(1.0 - residual / total) if total > 0.0 else np.nan,
        "count": int(len(x)),
    }


def compute_source_increment_decomposition(
    z_curr_a, z_curr_b, z_next_a, z_next_b,
    omega_a, omega_b, G_a, G_b, dh_a, dh_b, dt,
):
    """Decompose S_n = Delta z_{n+1} - Delta z_n into omega, G, dh components."""
    Delta_z_curr = z_curr_a - z_curr_b
    Delta_z_next = z_next_a - z_next_b
    S_exact = Delta_z_next - Delta_z_curr

    dphi_a = np.angle(z_next_a * np.conj(z_curr_a))
    dphi_b = np.angle(z_next_b * np.conj(z_curr_b))

    S_lin = 1j * dphi_a * z_curr_a - 1j * dphi_b * z_curr_b

    dphi_omega_a = dt * omega_a
    dphi_omega_b = dt * omega_b
    dphi_G_a = dt * G_a
    dphi_G_b = dt * G_b
    dphi_dh_a = -dh_a
    dphi_dh_b = -dh_b

    S_omega = 1j * dphi_omega_a * z_curr_a - 1j * dphi_omega_b * z_curr_b
    S_G = 1j * dphi_G_a * z_curr_a - 1j * dphi_G_b * z_curr_b
    S_dh = 1j * dphi_dh_a * z_curr_a - 1j * dphi_dh_b * z_curr_b

    S_reconstructed = S_omega + S_G + S_dh

    return {
        "S_exact_real": float(S_exact.real),
        "S_exact_imag": float(S_exact.imag),
        "S_exact_mag": float(abs(S_exact)),
        "S_lin_mag": float(abs(S_lin)),
        "S_omega_mag": float(abs(S_omega)),
        "S_G_mag": float(abs(S_G)),
        "S_dh_mag": float(abs(S_dh)),
        "S_reconstructed_mag": float(abs(S_reconstructed)),
        "lin_error": float(abs(S_exact - S_lin)),
        "recon_error": float(abs(S_lin - S_reconstructed)),
        "dphi_a": float(dphi_a),
        "dphi_b": float(dphi_b),
        "dphi_sep": float(dphi_a - dphi_b),
        "dphi_omega_a": float(dphi_omega_a),
        "dphi_omega_b": float(dphi_omega_b),
        "dphi_G_a": float(dphi_G_a),
        "dphi_G_b": float(dphi_G_b),
        "dphi_dh_a": float(dphi_dh_a),
        "dphi_dh_b": float(dphi_dh_b),
        "G_a": float(G_a),
        "G_b": float(G_b),
        "dh_a": float(dh_a),
        "dh_b": float(dh_b),
    }


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--npz", default=DEFAULT_NPZ)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", default=DEFAULT_SEED)
    parser.add_argument("--dt", type=float, default=DEFAULT_DT)
    parser.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON)
    parser.add_argument("--intervals", type=parse_nonnegative_float_list,
                        default=parse_nonnegative_float_list(DEFAULT_INTERVALS))
    parser.add_argument("--signal-floor", type=float, default=DEFAULT_SIGNAL_FLOOR)
    return parser.parse_args()


def main():
    args = parse_arguments()

    for path in (args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Required input '{path}' not found.")

    base, component_audit, augmented = load_production_modules()

    print(f"Loading production manifest: {args.manifest}")
    with open(args.manifest, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    model = manifest["model"]
    dt = float(model["dt"])
    if abs(dt - args.dt) > 1e-15:
        raise ValueError(f"dt mismatch: {args.dt} vs {dt}")

    alpha = math.exp(-dt / float(model["T_window"]))
    r_ema = -np.log(alpha) / dt
    omega_arr = np.asarray(model["omega"], dtype=float)
    capacity = (float(model["a"]) - float(model["delta"])) / float(model["q"])
    capacities = np.full(int(model["N"]), capacity)
    N = int(model["N"])

    A, edges = base.incidence_matrix(N)

    future_steps = int(manifest["protocol"]["future_steps"])
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)

    eps_scale = args.scale_epsilon
    time_vec = np.arange(future_steps) * dt

    # Two-pass replay: need z_n and z_{n+1} to compute S_n
    print("Replaying to capture source increments...")

    # Reload for clean pass
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)

    prev_z = {}
    prev_coupling = {}
    prev_dh = {}
    for ch in CHANNEL_EDGES:
        prev_z[ch] = {"fwd_a": 0j, "fwd_b": 0j, "rev_a": 0j, "rev_b": 0j}
        prev_coupling[ch] = {"fwd_Ga": 0.0, "fwd_Gb": 0.0, "rev_Ga": 0.0, "rev_Gb": 0.0}
        prev_dh[ch] = {"fwd_dha": 0.0, "fwd_dhb": 0.0, "rev_dha": 0.0, "rev_dhb": 0.0}

    rows = []
    first_step = True

    for step in range(future_steps):
        intermediate = augmented.base_intermediates(
            state, model, capacities, A, edges, eps_scale
        )

        phase_factor = intermediate["phase_factor"]
        coupling = intermediate["coupling"]

        history_arr = np.asarray(list(state.history), dtype=float)
        if len(history_arr) >= 2:
            dh_full = np.angle(np.exp(1j * (history_arr[1] - history_arr[0])))
        else:
            dh_full = np.zeros(N)

        curr_z = {}
        curr_coupling = {}
        curr_dh = {}
        curr_omega_pair = {}

        for ch_name, edges_ch in CHANNEL_EDGES.items():
            ia, ja = edges_ch["edge_a"]
            ib, jb = edges_ch["edge_b"]

            curr_z[ch_name] = {
                "fwd_a": phase_factor[ia, ja],
                "fwd_b": phase_factor[ib, jb],
                "rev_a": phase_factor[ja, ia],
                "rev_b": phase_factor[jb, ib],
            }
            curr_coupling[ch_name] = {
                "fwd_Ga": float(coupling[ia]),
                "fwd_Gb": float(coupling[ib]),
                "rev_Ga": float(coupling[ja]),
                "rev_Gb": float(coupling[jb]),
            }
            curr_dh[ch_name] = {
                "fwd_dha": float(dh_full[ja]),
                "fwd_dhb": float(dh_full[jb]),
                "rev_dha": float(dh_full[ia]),
                "rev_dhb": float(dh_full[ib]),
            }
            curr_omega_pair[ch_name] = {
                "fwd_wa": float(omega_arr[ia]),
                "fwd_wb": float(omega_arr[ib]),
                "rev_wa": float(omega_arr[ja]),
                "rev_wb": float(omega_arr[jb]),
            }

        if not first_step:
            for ch_name in CHANNEL_EDGES:
                for ori_label, keys in [
                    ("forward", ("fwd_a", "fwd_b", "fwd_Ga", "fwd_Gb",
                                 "fwd_dha", "fwd_dhb", "fwd_wa", "fwd_wb")),
                    ("reverse", ("rev_a", "rev_b", "rev_Ga", "rev_Gb",
                                 "rev_dha", "rev_dhb", "rev_wa", "rev_wb")),
                ]:
                    (z_key_a, z_key_b, G_key_a, G_key_b,
                     dh_key_a, dh_key_b, w_key_a, w_key_b) = keys

                    decomp = compute_source_increment_decomposition(
                        z_curr_a=prev_z[ch_name][z_key_a],
                        z_curr_b=prev_z[ch_name][z_key_b],
                        z_next_a=curr_z[ch_name][z_key_a],
                        z_next_b=curr_z[ch_name][z_key_b],
                        omega_a=curr_omega_pair[ch_name][w_key_a],
                        omega_b=curr_omega_pair[ch_name][w_key_b],
                        G_a=prev_coupling[ch_name][G_key_a],
                        G_b=prev_coupling[ch_name][G_key_b],
                        dh_a=prev_dh[ch_name][dh_key_a],
                        dh_b=prev_dh[ch_name][dh_key_b],
                        dt=dt,
                    )
                    row = {
                        "step": step,
                        "time": time_vec[step],
                        "channel": ch_name,
                        "orientation": ori_label,
                    }
                    row.update(decomp)
                    rows.append(row)

        prev_z = curr_z
        prev_coupling = curr_coupling
        prev_dh = curr_dh
        first_step = False

        augmented.advance_base_state(state, intermediate)

    df = pd.DataFrame(rows)

    # Interval analysis
    T_end = future_steps * dt
    boundaries = [b for b in args.intervals if 0.0 <= b <= T_end]
    if 0.0 not in boundaries:
        boundaries.insert(0, 0.0)
    if T_end not in boundaries:
        boundaries.append(T_end)
    boundaries = sorted(set(boundaries))

    interval_rows = []
    for ch_name in CHANNEL_EDGES:
        for ori_label in ["forward", "reverse"]:
            mask = (df["channel"] == ch_name) & (df["orientation"] == ori_label)
            sub = df[mask].copy()
            if len(sub) == 0:
                continue
            times_sub = sub["time"].values

            for i in range(len(boundaries) - 1):
                start_t, end_t = boundaries[i], boundaries[i + 1]
                s_mask = (times_sub >= start_t) & (times_sub < end_t)
                sub_int = sub[s_mask]
                if len(sub_int) < 3:
                    continue

                t_int = sub_int["time"].values
                S_fit = fit_log_rate(t_int, sub_int["S_exact_mag"].values, args.signal_floor)
                omega_fit = fit_log_rate(t_int, sub_int["S_omega_mag"].values, args.signal_floor)
                G_fit = fit_log_rate(t_int, sub_int["S_G_mag"].values, args.signal_floor)
                dh_fit = fit_log_rate(t_int, sub_int["S_dh_mag"].values, args.signal_floor)

                total_mag = sub_int["S_exact_mag"].values
                frac_omega = float(np.nanmedian(sub_int["S_omega_mag"].values / (total_mag + 1e-18)))
                frac_G = float(np.nanmedian(sub_int["S_G_mag"].values / (total_mag + 1e-18)))
                frac_dh = float(np.nanmedian(sub_int["S_dh_mag"].values / (total_mag + 1e-18)))

                interval_rows.append({
                    "channel": ch_name,
                    "orientation": ori_label,
                    "interval_start": start_t,
                    "interval_end": end_t,
                    "S_rate": S_fit["rate"],
                    "S_R2": S_fit["R_squared"],
                    "omega_component_rate": omega_fit["rate"],
                    "omega_component_R2": omega_fit["R_squared"],
                    "G_component_rate": G_fit["rate"],
                    "G_component_R2": G_fit["R_squared"],
                    "dh_component_rate": dh_fit["rate"],
                    "dh_component_R2": dh_fit["R_squared"],
                    "frac_omega_median": frac_omega,
                    "frac_G_median": frac_G,
                    "frac_dh_median": frac_dh,
                })

    interval_df = pd.DataFrame(interval_rows)

    # Output
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_atomic_write_csv(output_dir / "source_decomposition_trajectory.csv", df)
    safe_atomic_write_csv(output_dir / "source_decomposition_intervals.csv", interval_df)

    # Report
    lines = [
        "=" * 70,
        "AIEF-1.4 Phase-Increment Source Decomposition",
        "=" * 70,
        "",
        f"alpha_EMA: {alpha:.12g}",
        f"r_EMA:    {r_ema:.6f}",
        f"dt:       {dt}",
        "",
        "Decomposes S_n = Delta z_{n+1} - Delta z_n into:",
        "  1. Intrinsic frequency:  dt * (omega_a - omega_b)",
        "  2. Coupling:             dt * (G_a - G_b)",
        "  3. History:              -(Delta h_a - Delta h_b)",
        "",
        "Purpose: illuminate WHY S_n decays at the EMA rate.",
        "",
        "-" * 70,
        "Interval-by-Interval Component Rate Analysis",
        "-" * 70,
        "",
    ]

    for ch_name in CHANNEL_EDGES:
        for ori_label in ["forward", "reverse"]:
            lines.append(f"Channel: {ch_name} ({ori_label})")
            hdr = f"  {'Interval':<16} {'S_rate':>10} {'omega':>10} {'G':>10} {'dh':>10} {'frac_G':>10}"
            lines.append(hdr)
            lines.append(f"  {'-'*16} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
            mask = (interval_df["channel"] == ch_name) & (interval_df["orientation"] == ori_label)
            for _, row in interval_df[mask].iterrows():
                s = f"  [{row['interval_start']:.0f},{row['interval_end']:.0f})"
                lines.append(
                    f"  {s:<16} {row['S_rate']:>10.6f} {row['omega_component_rate']:>10.6f} "
                    f"{row['G_component_rate']:>10.6f} {row['dh_component_rate']:>10.6f} "
                    f"{row['frac_G_median']:>10.4f}"
                )
            lines.append("")

    # Late-window
    late_mask = df["time"] >= 250.0
    lines.extend([
        "-" * 70,
        "Late-Window (t >= 250) Component Magnitude Fractions (median)",
        "-" * 70,
        "",
    ])
    for ch_name in CHANNEL_EDGES:
        for ori_label in ["forward", "reverse"]:
            mask = late_mask & (df["channel"] == ch_name) & (df["orientation"] == ori_label)
            sub = df[mask]
            if len(sub) == 0:
                continue
            total = sub["S_exact_mag"].values
            f_omega = np.nanmedian(sub["S_omega_mag"].values / (total + 1e-18))
            f_G = np.nanmedian(sub["S_G_mag"].values / (total + 1e-18))
            f_dh = np.nanmedian(sub["S_dh_mag"].values / (total + 1e-18))
            lines.append(f"  {ch_name} {ori_label}: omega={f_omega:.4f}  G={f_G:.4f}  dh={f_dh:.4f}")

    lines.extend([
        "",
        "-" * 70,
        "Interpretation Guide",
        "-" * 70,
        "",
        "If G (coupling) dominates and its rate -> r_EMA, then coupling-mediated",
        "delayed-history feedback drives alignment-residual decay.",
        "",
        "If all components have comparable magnitude but S_n decays at r_EMA",
        "while components decay faster, cancellation produces the net rate.",
        "",
        "If omega is near-constant (rate ~0), intrinsic frequency difference",
        "provides static background; G and dh converge toward cancelling it.",
        "",
        "This is mechanism illumination, not a proof.",
        "Evidence class: diagnostic mechanism exploration.",
    ])

    report = "\n".join(lines)
    safe_atomic_write_text(output_dir / "source_decomposition_report.txt", report)

    manifest_output = {
        "analysis": "AIEF-1.4 phase-increment source decomposition",
        "evidence_class": "diagnostic mechanism exploration",
        "production_run_hash": DEFAULT_RUN_HASH,
        "seed": args.seed,
        "parameters": {
            "dt": dt,
            "alpha_EMA": alpha,
            "r_EMA": r_ema,
            "scale_epsilon": args.scale_epsilon,
            "signal_floor": args.signal_floor,
            "intervals": boundaries,
        },
        "outputs": [
            "source_decomposition_trajectory.csv",
            "source_decomposition_intervals.csv",
            "source_decomposition_report.txt",
            "analysis_manifest.json",
        ],
        "not_a_proof": True,
        "open_problem": (
            "Deriving alpha-rate alignment-residual decay from the coupled "
            "phase, delayed-history, EMA, and weight dynamics"
        ),
    }

    safe_atomic_write_text(
        output_dir / "analysis_manifest.json",
        json.dumps(manifest_output, indent=2) + "\n",
    )

    print(report)
    print(f"\n[SUCCESS] Artifacts saved to: '{output_dir.resolve()}'")


if __name__ == "__main__":
    main()
