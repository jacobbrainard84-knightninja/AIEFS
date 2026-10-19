#!/usr/bin/env python3

"""
AIEF-1.4 Phase-Increment Cancellation Audit (v2)

Tests the hypothesis that the upstream source-increment decay at the EMA rate
arises from cancellation between three individually-O(1) phase contributions:

  Delta phi_sep = phi_omega + phi_G + phi_h

where:
  phi_omega = dt * (omega_ia - omega_ib)     [intrinsic frequency separation]
  phi_G     = dt * (G_ia,n - G_ib,n)          [coupling separation]
  phi_h     = -(dh_ja,n - dh_jb,n)            [history separation]

For each step, computes:
  - Residual epsilon = phi_omega + phi_G + phi_h
  - Cancellation index: |epsilon| / (|phi_omega| + |phi_G| + |phi_h|)
  - Pairwise angles between the three component vectors (in 2D phase space)
  - Individual component magnitudes and their decay rates

A cancellation index << 1 means the three terms nearly cancel, analogous to
the downstream alignment-residual cancellation T1 ≈ -T2.

This is mechanism illumination, not a proof.

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
DEFAULT_OUTPUT_DIR = "aief_1_4_phase_cancellation_audit"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_SIGNAL_FLOOR = 1e-14
DEFAULT_INTERVALS = "0,50,100,150,200,250,300,320"

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
    """Fit exponential decay rate from log magnitudes. Returns nan if <3 valid points."""
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


def compute_phase_cancellation(
    omega_a, omega_b, G_a, G_b, dh_a, dh_b, dt,
):
    """
    Decompose the phase separation increment:

      Delta phi_sep = phi_omega + phi_G + phi_h

    where each term is the separation (edge_a minus edge_b) of the
    corresponding phase-increment component.

    Returns component magnitudes, residual, cancellation index, and
    pairwise angles between the three component vectors.
    """
    # Phase increment components for each edge
    dphi_omega_a = dt * omega_a
    dphi_omega_b = dt * omega_b
    dphi_G_a = dt * G_a
    dphi_G_b = dt * G_b
    dphi_h_a = -dh_a
    dphi_h_b = -dh_b

    # Separation (edge_a minus edge_b) for each component
    phi_omega = dphi_omega_a - dphi_omega_b
    phi_G = dphi_G_a - dphi_G_b
    phi_h = dphi_h_a - dphi_h_b

    # Total phase separation increment
    phi_total = phi_omega + phi_G + phi_h

    # Magnitudes
    abs_omega = abs(phi_omega)
    abs_G = abs(phi_G)
    abs_h = abs(phi_h)
    abs_total = abs(phi_total)
    denom = abs_omega + abs_G + abs_h + 1e-300

    # Cancellation index: |epsilon| / (|phi_omega| + |phi_G| + |phi_h|)
    # Small value => strong cancellation
    canc_idx = abs_total / denom

    # Pairwise angles between component vectors (in 1D signed space,
    # angle is just sign agreement: cos(theta) = sign(x)*sign(y))
    # For a richer picture, embed in 2D: treat each phi as vector (phi, 0)
    # Then angle between phi_omega and phi_G is 0 or pi depending on sign.
    # More useful: report the signed values directly and the "alignment"
    # between the sum of first two and the third.
    sum_omega_G = phi_omega + phi_G
    abs_sum_omega_G = abs(sum_omega_G)

    # Cancellation between omega+G and h
    canc_omegaG_vs_h = (
        abs(sum_omega_G + phi_h) / (abs_sum_omega_G + abs_h + 1e-300)
    )

    # Sign pattern: which components oppose which
    sign_omega = 1 if phi_omega > 0 else (-1 if phi_omega < 0 else 0)
    sign_G = 1 if phi_G > 0 else (-1 if phi_G < 0 else 0)
    sign_h = 1 if phi_h > 0 else (-1 if phi_h < 0 else 0)

    # Fraction of total absolute contribution from each component
    frac_omega = abs_omega / denom
    frac_G = abs_G / denom
    frac_h = abs_h / denom

    return {
        # Component values (signed)
        "phi_omega": float(phi_omega),
        "phi_G": float(phi_G),
        "phi_h": float(phi_h),
        "phi_total": float(phi_total),
        # Absolute magnitudes
        "abs_phi_omega": float(abs_omega),
        "abs_phi_G": float(abs_G),
        "abs_phi_h": float(abs_h),
        "abs_phi_total": float(abs_total),
        # Cancellation metrics
        "cancellation_index": float(canc_idx),
        "canc_omegaG_vs_h": float(canc_omegaG_vs_h),
        # Sign pattern
        "sign_omega": int(sign_omega),
        "sign_G": int(sign_G),
        "sign_h": int(sign_h),
        # Components as fractions of total absolute sum
        "frac_omega": float(frac_omega),
        "frac_G": float(frac_G),
        "frac_h": float(frac_h),
        # Raw per-edge values for reference
        "dphi_omega_a": float(dphi_omega_a),
        "dphi_omega_b": float(dphi_omega_b),
        "dphi_G_a": float(dphi_G_a),
        "dphi_G_b": float(dphi_G_b),
        "dphi_h_a": float(dphi_h_a),
        "dphi_h_b": float(dphi_h_b),
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

    print("Replaying to capture phase-increment components...")

    rows = []
    first_step = True

    # Store previous coupling and dh for computing increments
    prev_coupling = {}
    prev_dh = {}
    for ch in CHANNEL_EDGES:
        prev_coupling[ch] = {}
        prev_dh[ch] = {}

    for step in range(future_steps):
        intermediate = augmented.base_intermediates(
            state, model, capacities, A, edges, eps_scale
        )

        coupling = intermediate["coupling"]

        history_arr = np.asarray(list(state.history), dtype=float)
        if len(history_arr) >= 2:
            dh_full = np.angle(np.exp(1j * (history_arr[1] - history_arr[0])))
        else:
            dh_full = np.zeros(N)

        curr_coupling = {}
        curr_dh = {}
        curr_omega_pair = {}

        for ch_name, edges_ch in CHANNEL_EDGES.items():
            ia, ja = edges_ch["edge_a"]
            ib, jb = edges_ch["edge_b"]

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
                    ("forward", ("fwd_Ga", "fwd_Gb", "fwd_dha", "fwd_dhb",
                                 "fwd_wa", "fwd_wb")),
                    ("reverse", ("rev_Ga", "rev_Gb", "rev_dha", "rev_dhb",
                                 "rev_wa", "rev_wb")),
                ]:
                    (G_key_a, G_key_b, dh_key_a, dh_key_b,
                     w_key_a, w_key_b) = keys

                    # Use coupling from step n (prev) and dh from step n (prev)
                    # to predict the phase increment from step n to step n+1.
                    # The phase increment at step n uses the state at step n:
                    #   dphi = dt*omega + dt*G_n - dh_n
                    # where G_n comes from the coupling computed at step n
                    # (which uses B_{n+1} per implementation).
                    # We stored coupling at step n (from intermediate at step n),
                    # and dh is the history change that will produce step n+1.
                    decomp = compute_phase_cancellation(
                        omega_a=curr_omega_pair[ch_name][w_key_a],
                        omega_b=curr_omega_pair[ch_name][w_key_b],
                        G_a=curr_coupling[ch_name][G_key_a],
                        G_b=curr_coupling[ch_name][G_key_b],
                        dh_a=curr_dh[ch_name][dh_key_a],
                        dh_b=curr_dh[ch_name][dh_key_b],
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

        prev_coupling = curr_coupling
        prev_dh = curr_dh
        first_step = False

        augmented.advance_base_state(state, intermediate)

    df = pd.DataFrame(rows)

    # --- Interval analysis ---
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

                # Fit rates for absolute component magnitudes
                omega_rate = fit_log_rate(t_int, sub_int["abs_phi_omega"].values, args.signal_floor)
                G_rate = fit_log_rate(t_int, sub_int["abs_phi_G"].values, args.signal_floor)
                h_rate = fit_log_rate(t_int, sub_int["abs_phi_h"].values, args.signal_floor)
                total_rate = fit_log_rate(t_int, sub_int["abs_phi_total"].values, args.signal_floor)

                # Cancellation index (median over interval)
                canc_med = float(np.nanmedian(sub_int["cancellation_index"].values))
                canc_omegaG_h_med = float(np.nanmedian(sub_int["canc_omegaG_vs_h"].values))

                # Component fractions (median)
                frac_omega = float(np.nanmedian(sub_int["frac_omega"].values))
                frac_G = float(np.nanmedian(sub_int["frac_G"].values))
                frac_h = float(np.nanmedian(sub_int["frac_h"].values))

                # Sign agreement: fraction of steps where omega and G have same sign
                same_sign_omega_G = float(np.mean(
                    sub_int["sign_omega"].values == sub_int["sign_G"].values
                ))
                same_sign_omega_h = float(np.mean(
                    sub_int["sign_omega"].values == sub_int["sign_h"].values
                ))
                same_sign_G_h = float(np.mean(
                    sub_int["sign_G"].values == sub_int["sign_h"].values
                ))

                # Median absolute component values (not rates)
                med_abs_omega = float(np.nanmedian(sub_int["abs_phi_omega"].values))
                med_abs_G = float(np.nanmedian(sub_int["abs_phi_G"].values))
                med_abs_h = float(np.nanmedian(sub_int["abs_phi_h"].values))
                med_abs_total = float(np.nanmedian(sub_int["abs_phi_total"].values))

                interval_rows.append({
                    "channel": ch_name,
                    "orientation": ori_label,
                    "interval_start": start_t,
                    "interval_end": end_t,
                    "total_rate": total_rate["rate"],
                    "total_R2": total_rate["R_squared"],
                    "omega_rate": omega_rate["rate"],
                    "G_rate": G_rate["rate"],
                    "h_rate": h_rate["rate"],
                    "cancellation_index_median": canc_med,
                    "canc_omegaG_vs_h_median": canc_omegaG_h_med,
                    "frac_omega_median": frac_omega,
                    "frac_G_median": frac_G,
                    "frac_h_median": frac_h,
                    "same_sign_omega_G": same_sign_omega_G,
                    "same_sign_omega_h": same_sign_omega_h,
                    "same_sign_G_h": same_sign_G_h,
                    "med_abs_phi_omega": med_abs_omega,
                    "med_abs_phi_G": med_abs_G,
                    "med_abs_phi_h": med_abs_h,
                    "med_abs_phi_total": med_abs_total,
                })

    interval_df = pd.DataFrame(interval_rows)

    # --- Output ---
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_atomic_write_csv(output_dir / "phase_cancellation_trajectory.csv", df)
    safe_atomic_write_csv(output_dir / "phase_cancellation_intervals.csv", interval_df)

    # --- Build report ---
    r_ema_str = f"{r_ema:.6f}"
    lines = [
        "=" * 70,
        "AIEF-1.4 Phase-Increment Cancellation Audit (v2)",
        "=" * 70,
        "",
        f"alpha_EMA: {alpha:.12g}",
        f"r_EMA:    {r_ema_str}",
        f"dt:       {dt}",
        "",
        "Tests: does the source-increment decay arise from cancellation",
        "between three individually-O(1) phase contributions?",
        "",
        "  Delta phi_sep = phi_omega + phi_G + phi_h",
        "",
        "  phi_omega = dt*(omega_ia - omega_ib)   [intrinsic, constant]",
        "  phi_G     = dt*(G_ia,n - G_ib,n)        [coupling, dynamic]",
        "  phi_h     = -(dh_ja,n - dh_jb,n)        [history, dynamic]",
        "",
        "Cancellation index = |phi_total| / (|phi_omega| + |phi_G| + |phi_h|)",
        "  index << 1  =>  strong cancellation (analogous to T1 ~= -T2)",
        "  index ~ 1   =>  one component dominates or no cancellation",
        "",
        "-" * 70,
        "Interval-by-Interval Analysis",
        "-" * 70,
        "",
    ]

    for ch_name in CHANNEL_EDGES:
        for ori_label in ["forward", "reverse"]:
            lines.append(f"Channel: {ch_name} ({ori_label})")
            hdr = (
                f"  {'Interval':<16} {'|eps|':>10} {'|omega|':>10} {'|G|':>10} "
                f"{'|dh|':>10} {'CancIdx':>10} {'omegaG_v_h':>12}"
            )
            lines.append(hdr)
            lines.append(f"  {'-'*16} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*12}")
            mask = (interval_df["channel"] == ch_name) & (interval_df["orientation"] == ori_label)
            for _, row in interval_df[mask].iterrows():
                s = f"  [{row['interval_start']:.0f},{row['interval_end']:.0f})"
                lines.append(
                    f"  {s:<16} {row['med_abs_phi_total']:>10.6e} "
                    f"{row['med_abs_phi_omega']:>10.6e} {row['med_abs_phi_G']:>10.6e} "
                    f"{row['med_abs_phi_h']:>10.6e} {row['cancellation_index_median']:>10.6e} "
                    f"{row['canc_omegaG_vs_h_median']:>12.6e}"
                )
            lines.append("")

            # Also show rates
            lines.append(f"  Decay rates for absolute component magnitudes:")
            hdr2 = (
                f"  {'Interval':<16} {'total_rate':>12} {'omega_rate':>12} "
                f"{'G_rate':>12} {'h_rate':>12}"
            )
            lines.append(hdr2)
            lines.append(f"  {'-'*16} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")
            for _, row in interval_df[mask].iterrows():
                s = f"  [{row['interval_start']:.0f},{row['interval_end']:.0f})"
                lines.append(
                    f"  {s:<16} {row['total_rate']:>12.6f} {row['omega_rate']:>12.6f} "
                    f"{row['G_rate']:>12.6f} {row['h_rate']:>12.6f}"
                )
            lines.append("")

            # Sign agreement
            lines.append(f"  Sign agreement fractions:")
            for _, row in interval_df[mask].iterrows():
                s = f"  [{row['interval_start']:.0f},{row['interval_end']:.0f})"
                lines.append(
                    f"  {s:<16} omega-G: {row['same_sign_omega_G']:.3f}  "
                    f"omega-h: {row['same_sign_omega_h']:.3f}  "
                    f"G-h: {row['same_sign_G_h']:.3f}"
                )
            lines.append("")

    # Late-window summary
    late_mask = df["time"] >= 250.0
    lines.extend([
        "-" * 70,
        "Late-Window (t >= 250) Summary (median over all late steps)",
        "-" * 70,
        "",
    ])
    for ch_name in CHANNEL_EDGES:
        for ori_label in ["forward", "reverse"]:
            mask = late_mask & (df["channel"] == ch_name) & (df["orientation"] == ori_label)
            sub = df[mask]
            if len(sub) == 0:
                continue
            canc = np.nanmedian(sub["cancellation_index"].values)
            canc_og_h = np.nanmedian(sub["canc_omegaG_vs_h"].values)
            abs_om = np.nanmedian(sub["abs_phi_omega"].values)
            abs_G = np.nanmedian(sub["abs_phi_G"].values)
            abs_h = np.nanmedian(sub["abs_phi_h"].values)
            abs_tot = np.nanmedian(sub["abs_phi_total"].values)
            lines.append(f"  {ch_name} {ori_label}:")
            lines.append(f"    |phi_omega| = {abs_om:.6e}")
            lines.append(f"    |phi_G|     = {abs_G:.6e}")
            lines.append(f"    |phi_h|     = {abs_h:.6e}")
            lines.append(f"    |phi_total| = {abs_tot:.6e}")
            lines.append(f"    Cancellation index  = {canc:.6e}")
            lines.append(f"    omega+G vs h index  = {canc_og_h:.6e}")
            lines.append("")

    lines.extend([
        "-" * 70,
        "Interpretation Guide",
        "-" * 70,
        "",
        "If cancellation_index << 1 while individual |phi_*| remain O(1),",
        "the three phase components nearly cancel.  The EMA-rate decay of",
        "the net source increment S_n then arises from this cancellation",
        "at the phase level, not from any single component's decay.",
        "",
        "If cancellation_index -> 0 monotonically, the cancellation is",
        "tightening over time — consistent with the system approaching",
        "a phase-locked asymptotic regime.",
        "",
        "If canc_omegaG_vs_h << canc_index, the primary cancellation is",
        "between (omega+G) and h — i.e., the coupling tracks the intrinsic",
        "frequency, and history opposes their sum.",
        "",
        "Compare with downstream: T1 ~= -T2 at the alignment layer.",
        "If both layers show cancellation, the structural motif is:",
        "  phase level:  omega + G + dh ~= 0",
        "  alignment:    T1 + T2 ~= 0",
        "  proposal:     exact stable recurrence (forced).",
        "",
        "This is mechanism illumination, not a proof.",
        "Evidence class: diagnostic mechanism exploration.",
    ])

    report = "\n".join(lines)
    safe_atomic_write_text(output_dir / "phase_cancellation_report.txt", report)

    manifest_output = {
        "analysis": "AIEF-1.4 phase-increment cancellation audit v2",
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
            "phase_cancellation_trajectory.csv",
            "phase_cancellation_intervals.csv",
            "phase_cancellation_report.txt",
            "analysis_manifest.json",
        ],
        "not_a_proof": True,
        "method": (
            "Decomposes phase separation increment (before exponentiation) "
            "into omega, G, and dh components.  Computes cancellation index "
            "|phi_total| / (|phi_omega| + |phi_G| + |phi_h|)."
        ),
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
