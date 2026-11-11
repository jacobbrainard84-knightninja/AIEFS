#!/usr/bin/env python3

"""
AIEF-1.4 Transverse Phase Jacobian — Decisive Calculation

Tests:  Is the phase synchronization rate faster than the EMA memory rate?

The system converges to a synchronized manifold:
    omega_i + G_i -> Omega   (same effective frequency for all K3 nodes).

The transverse (relative-phase) contraction is governed by the graph Laplacian
of the weighted coupling matrix W:
    W_{ik} = B_{ik} * cos(h_k - theta_i)
    L_W = D - W   where D_{ii} = sum_k W_{ik}

    d(delta_theta)/dt = -L_W * delta_theta

The common mode (1,1,1) is in the kernel.  The non-zero eigenvalues s_1, s_2
of -L_W determine the transverse contraction rates:
    mu_phase = -max(Re(s_1), Re(s_2))

If mu_phase > r_EMA = -log(alpha)/dt = 0.057133, then phase synchronization
is faster than the EMA memory.  The EMA pole is the bottleneck, and all
downstream observables inherit r_EMA from the single slow mode.

If mu_phase <= r_EMA, phase synchronization is the bottleneck, and the
interpretation must be revised.

No interpretation is forced.  The eigenvalues speak.
"""

from __future__ import annotations

import argparse, hashlib, json, math, os, sys, tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_transverse_phase_jacobian"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_SIGNAL_FLOOR = 1e-14

K3_ORDER = [2, 7, 11]           # node ordering for 3x3 matrices
K3_EDGE_LIST = [(2,7,25), (2,11,29), (7,11,59)]

def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as h:
        while b := h.read(1024*1024):
            d.update(b)
    return d.hexdigest()

def compute_module_sha256(m):
    if m is None or not hasattr(m, "__file__") or m.__file__ is None:
        return "not_available"
    return file_sha256(Path(m.__file__).resolve())

def load_production_modules():
    import AIEF_1_4_stationarity_perturbation_analysis_updated as base
    import AIEF_1_4_component_controller_audit as ca
    import AIEF_1_4_augmented_tangent_cocycle_analysis as aug
    return base, ca, aug

def safe_atomic_write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tp = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content); f.flush(); os.fsync(f.fileno())
        os.replace(tp, path)
    except Exception:
        if os.path.exists(tp): os.remove(tp)
        raise

def safe_atomic_write_csv(path, df):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tp = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            df.to_csv(f, index=False); f.flush(); os.fsync(f.fileno())
        os.replace(tp, path)
    except Exception:
        if os.path.exists(tp): os.remove(tp)
        raise

def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--npz", default=DEFAULT_NPZ)
    p.add_argument("--manifest", default=DEFAULT_MANIFEST)
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--seed", default=DEFAULT_SEED)
    p.add_argument("--dt", type=float, default=DEFAULT_DT)
    p.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON)
    p.add_argument("--signal-floor", type=float, default=DEFAULT_SIGNAL_FLOOR)
    return p.parse_args()

def main():
    args = parse_args()
    for path in (args.npz, args.manifest):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Missing: {path}")

    base, ca, aug = load_production_modules()
    with open(args.manifest) as h:
        manifest = json.load(h)
    model = manifest["model"]
    dt = float(model["dt"])
    alpha = math.exp(-dt/float(model["T_window"]))
    r_ema = -np.log(alpha)/dt

    omega_arr = np.asarray(model["omega"], dtype=float)
    cap = (float(model["a"])-float(model["delta"]))/float(model["q"])
    caps = np.full(int(model["N"]), cap)
    N = int(model["N"])
    A, edges = base.incidence_matrix(N)
    fs = int(manifest["protocol"]["future_steps"])
    eps_sc = args.scale_epsilon
    tau_delay = 0.5

    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)

    time_vec = np.arange(fs) * dt
    rows = []

    for step in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges, eps_sc)

        B_mat = state.B
        pf = inter["phase_factor"]

        history_list = list(state.history)
        h_arr = history_list[0] if len(history_list) > 0 else np.zeros(N)

        # Reconstruct theta_i for K3 nodes from phase_factor
        theta = np.zeros(N)
        for node_i, partner in [(2,7), (7,2), (11,2)]:
            const_ik = 0.5*(omega_arr[node_i]+omega_arr[partner])*tau_delay
            theta[node_i] = float(np.angle(pf[node_i,partner])+h_arr[partner]+const_ik)

        # Build 3x3 weighted coupling matrix W_{ik} = B_{ik}*cos(h_k-theta_i)
        # Index map: node 2->0, 7->1, 11->2
        idx = {2:0, 7:1, 11:2}
        W = np.zeros((3,3))
        for ia, ib, _ in K3_EDGE_LIST:
            i, j = idx[ia], idx[ib]
            phase_diff_ij = h_arr[ib] - theta[ia]
            cos_ij = math.cos(phase_diff_ij)
            w_ij = float(B_mat[ia, ib]) * cos_ij

            phase_diff_ji = h_arr[ia] - theta[ib]
            cos_ji = math.cos(phase_diff_ji)
            w_ji = float(B_mat[ib, ia]) * cos_ji

            W[i,j] = w_ij
            W[j,i] = w_ji

        # Graph Laplacian L_W = D - W
        D_vec = np.sum(W, axis=1)
        L_W = np.diag(D_vec) - W

        # Jacobian = -L_W
        J = -L_W

        # Eigenvalues
        evals = np.linalg.eigvals(J)
        # Sort: real part closest to zero first
        evals_sorted = sorted(evals, key=lambda x: x.real, reverse=True)

        common_mode_eval = evals_sorted[0]   # should be ~0
        s1 = evals_sorted[1]
        s2 = evals_sorted[2]

        mu_phase = -max(s1.real, s2.real)   # slowest transverse rate
        # In continuous time, perturbations ~ exp(s_k * t).
        # The slowest decaying non-zero mode has the eigenvalue with the
        # largest (least negative) real part.  mu_phase is the positive
        # rate at which it decays.

        # Per-step discrete contraction factor for transverse modes:
        # exp(-mu_phase * dt) is the per-step factor.
        # Compare to alpha = exp(-r_ema * dt).
        discrete_factor = math.exp(-mu_phase * dt) if mu_phase > 0 else 1.0
        ema_faster = mu_phase > r_ema

        rows.append({
            "step": step, "time": time_vec[step],
            "eval_0_real": float(evals_sorted[0].real),
            "eval_0_imag": float(evals_sorted[0].imag),
            "eval_1_real": float(s1.real),
            "eval_1_imag": float(s1.imag),
            "eval_2_real": float(s2.real),
            "eval_2_imag": float(s2.imag),
            "mu_phase": float(mu_phase),
            "discrete_factor": float(discrete_factor),
            "r_ema": r_ema,
            "alpha": alpha,
            "ema_faster": bool(ema_faster),
            "W_27": float(W[0,1]), "W_72": float(W[1,0]),
            "W_2_11": float(W[0,2]), "W_11_2": float(W[2,0]),
            "W_7_11": float(W[1,2]), "W_11_7": float(W[2,1]),
            "D_2": float(D_vec[0]), "D_7": float(D_vec[1]), "D_11": float(D_vec[2]),
            "cos_27": float(math.cos(h_arr[7]-theta[2])),
            "cos_72": float(math.cos(h_arr[2]-theta[7])),
            "cos_2_11": float(math.cos(h_arr[11]-theta[2])),
            "cos_11_2": float(math.cos(h_arr[2]-theta[11])),
            "cos_7_11": float(math.cos(h_arr[11]-theta[7])),
            "cos_11_7": float(math.cos(h_arr[7]-theta[11])),
        })

        aug.advance_base_state(state, inter)

    df = pd.DataFrame(rows)

    # --- Interval analysis ---
    intervals = [(0,50),(50,100),(100,150),(150,200),(200,250),(250,300),(300,320)]
    int_rows = []
    for (a,b) in intervals:
        mask = (df["time"] >= a) & (df["time"] < b)
        chunk = df[mask]
        if len(chunk) < 3: continue
        int_rows.append({
            "interval_start": a, "interval_end": b,
            "mu_phase_median": float(np.nanmedian(chunk["mu_phase"])),
            "mu_phase_final": float(chunk["mu_phase"].iloc[-1]),
            "eval_1_real_median": float(np.nanmedian(chunk["eval_1_real"])),
            "eval_2_real_median": float(np.nanmedian(chunk["eval_2_real"])),
            "discrete_factor_median": float(np.nanmedian(chunk["discrete_factor"])),
            "ema_faster_fraction": float(np.mean(chunk["ema_faster"])),
            "D_2_median": float(np.nanmedian(chunk["D_2"])),
            "D_7_median": float(np.nanmedian(chunk["D_7"])),
            "D_11_median": float(np.nanmedian(chunk["D_11"])),
        })
    idf = pd.DataFrame(int_rows)

    # --- Output ---
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)
    safe_atomic_write_csv(od/"transverse_jacobian_trajectory.csv", df)
    safe_atomic_write_csv(od/"transverse_jacobian_intervals.csv", idf)

    # Final values
    final = df.iloc[-1]
    late = df[df["time"] >= 250.0]
    mu_late_med = float(np.nanmedian(late["mu_phase"]))
    ema_faster_late = float(np.mean(late["ema_faster"]))

    # --- Report ---
    lines = [
        "="*70,
        "AIEF-1.4 Transverse Phase Jacobian — Decisive Calculation",
        "="*70,
        "",
        f"r_EMA:  {r_ema:.6f}   alpha: {alpha:.12g}   dt: {dt}",
        "",
        "Question: Is phase synchronization faster than EMA memory?",
        "",
        "Method: Build the 3x3 weighted coupling matrix W_ik = B_ik*cos(h_k-theta_i)",
        "        for K3 nodes (2,7,11).  Form the graph Laplacian L_W = D - W.",
        "        The Jacobian of the relative phase dynamics is J = -L_W.",
        "        Non-zero eigenvalues of J give transverse contraction rates.",
        "        mu_phase = -max(Re(s_1), Re(s_2)) is the slowest transverse rate.",
        "",
        "        Compare:  mu_phase  vs  r_EMA = 0.057133",
        "",
        "        If mu_phase > r_EMA: synchronization faster -> EMA is bottleneck.",
        "        If mu_phase <= r_EMA: synchronization is bottleneck.",
        "",
        "-"*70,
        "Eigenvalues at Final Step (t=320):",
        "-"*70,
        f"  Common mode: {final['eval_0_real']:.6e} + {final['eval_0_imag']:.6e}i",
        f"  Transverse 1: {final['eval_1_real']:.6e} + {final['eval_1_imag']:.6e}i",
        f"  Transverse 2: {final['eval_2_real']:.6e} + {final['eval_2_imag']:.6e}i",
        "",
        f"  mu_phase (slowest transverse rate): {final['mu_phase']:.6f}",
        f"  r_EMA:                              {r_ema:.6f}",
        f"  mu_phase > r_EMA:                   {final['ema_faster']}",
        "",
        f"  Per-step discrete factor:  {final['discrete_factor']:.12g}",
        f"  EMA alpha:                 {alpha:.12g}",
        "",
        "-"*70,
        "Late-Window (t >= 250) Summary:",
        "-"*70,
        f"  mu_phase median:  {mu_late_med:.6f}",
        f"  EMA-faster fraction: {ema_faster_late:.3f}",
        "",
        "-"*70,
        "Interval Analysis:",
        "-"*70,
        f"  {'Interval':<16} {'mu_phase':>10} {'eval1_re':>12} {'eval2_re':>12} "
        f"{'disc_factor':>12} {'ema_faster':>10}",
        f"  {'-'*16} {'-'*10} {'-'*12} {'-'*12} {'-'*12} {'-'*10}",
    ]
    for _, r in idf.iterrows():
        lines.append(
            f"  [{r['interval_start']:>3.0f},{r['interval_end']:<3.0f})     "
            f"{r['mu_phase_median']:>10.6f} {r['eval_1_real_median']:>12.6e} "
            f"{r['eval_2_real_median']:>12.6e} {r['discrete_factor_median']:>12.6e} "
            f"{r['ema_faster_fraction']:>10.3f}"
        )

    lines.extend([
        "",
        "-"*70,
        "Weighted Coupling Matrix W (final step):",
        "-"*70,
        f"  W_27 = {final['W_27']:.6e}    W_72 = {final['W_72']:.6e}",
        f"  W_2_11 = {final['W_2_11']:.6e}  W_11_2 = {final['W_11_2']:.6e}",
        f"  W_7_11 = {final['W_7_11']:.6e}  W_11_7 = {final['W_11_7']:.6e}",
        "",
        f"  Row sums:  D_2={final['D_2']:.6e}  D_7={final['D_7']:.6e}  D_11={final['D_11']:.6e}",
        "",
        "-"*70,
        "cos(h_k - theta_i) values (final step):",
        "-"*70,
        f"  cos_27={final['cos_27']:.6e}    cos_72={final['cos_72']:.6e}",
        f"  cos_2_11={final['cos_2_11']:.6e}  cos_11_2={final['cos_11_2']:.6e}",
        f"  cos_7_11={final['cos_7_11']:.6e}  cos_11_7={final['cos_11_7']:.6e}",
        "",
        "-"*70,
        "Verdict:",
        "-"*70,
    ])

    if ema_faster_late > 0.99:
        lines.append("  CONFIRMED: mu_phase > r_EMA at essentially every late step.")
        lines.append("  Phase synchronization is faster than EMA memory.")
        lines.append("  The EMA pole is the bottleneck.  All downstream observables")
        lines.append("  inherit r_EMA = 0.057133 from the single slow transverse mode.")
    elif ema_faster_late > 0.5:
        lines.append("  MIXED: mu_phase > r_EMA at some steps but not all.")
        lines.append("  Further investigation needed.")
    else:
        lines.append("  REFUTED: mu_phase <= r_EMA.  Phase synchronization is NOT")
        lines.append("  faster than EMA memory.  The bottleneck interpretation")
        lines.append("  is incorrect.  Something else governs the observed r_EMA rate.")

    lines.extend([
        "",
        "Evidence class: diagnostic mechanism exploration.",
        "No interpretation is forced.  The eigenvalues speak.",
    ])

    report = "\n".join(lines)
    safe_atomic_write_text(od/"transverse_jacobian_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 transverse phase Jacobian",
        "evidence_class": "diagnostic mechanism exploration",
        "seed": args.seed,
        "parameters": {"dt":dt, "r_EMA":r_ema, "alpha":alpha, "tau_delay":tau_delay},
        "outputs": ["transverse_jacobian_trajectory.csv",
                     "transverse_jacobian_intervals.csv",
                     "transverse_jacobian_report.txt",
                     "analysis_manifest.json"],
        "tested_hypothesis": "mu_phase > r_EMA (phase sync faster than EMA memory)",
        "not_a_proof": True,
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")
    print(report)
    print(f"\n[SUCCESS] Artifacts saved to: '{od.resolve()}'")

if __name__ == "__main__":
    main()
