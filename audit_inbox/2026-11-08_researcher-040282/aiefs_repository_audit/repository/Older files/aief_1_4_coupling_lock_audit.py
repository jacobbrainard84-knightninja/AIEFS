#!/usr/bin/env python3

"""
AIEF-1.4 Coupling-Lock Audit

Directly tests the hypothesis that the adaptive coupling G_i compensates the
intrinsic frequency omega_i:

    G_i(B, theta, h) + omega_i -> 0

where:
    G_i = sum_k B_{ik,n+1} * sin(h_{k,n} - theta_{i,n})

For each K3 node (2, 7, 11), this script:
1.  Tracks the lock error:  eps_i = omega_i + G_i
2.  Decomposes G_i into per-edge contributions
3.  Tracks B, sin(h_k - theta_i), and their product per edge
4.  Fits decay rates on |eps_i| per interval
5.  Reports which edges carry the compensation and how it is achieved
    (weight adjustment vs. phase alignment vs. both)

No interpretation is forced.  The numbers speak.

Evidence class: diagnostic mechanism exploration.
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
DEFAULT_OUTPUT_DIR = "aief_1_4_coupling_lock_audit"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_SIGNAL_FLOOR = 1e-14

# K3 nodes and their incident edges (by edge index)
# Node 2: edges 25=(2,7), 29=(2,11)  [plus reverse: 25=(7,2)? No, edges are undirected.
#  B is symmetric, B[2,7]=B[7,2]=B[25].  G uses B_{ik} which is the weight from i to k.
#  In the undirected unique-edge representation, B_{i,k} = B[edge(i,k)].
#  But the coupling G sums over k using the weight TO node k from node i.
#  In the implemented code, B is a symmetric NxN matrix.  G_i = sum_k B[i,k] * sin(h_k - theta_i).
#  So B[i,k] is the symmetric weight.]

# Edges incident to each K3 node (by node pair, which maps to unique edge index)
NODE_EDGES = {
    2: [(7, 25), (11, 29)],   # (target_node, edge_index)
    7: [(2, 25), (11, 59)],
    11: [(2, 29), (7, 59)],
}


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


def fit_log_rate(t, v, floor, min_points=3):
    m = np.abs(np.asarray(v, dtype=float))
    ok = np.isfinite(m) & (m > floor)
    if np.sum(ok) < min_points:
        return {"rate": np.nan, "R2": np.nan, "n": int(np.sum(ok))}
    x = np.asarray(t, dtype=float)[ok]
    y = np.log(m[ok])
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    res = float(np.sum((y - pred)**2))
    tot = float(np.sum((y - np.mean(y))**2))
    return {"rate": float(-slope),
            "R2": float(1 - res/tot) if tot > 0 else np.nan,
            "n": int(len(x))}


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
    cap = (float(model["a"]) - float(model["delta"]))/float(model["q"])
    caps = np.full(int(model["N"]), cap)
    N = int(model["N"])
    A, edges = base.incidence_matrix(N)
    fs = int(manifest["protocol"]["future_steps"])
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)
    eps = args.scale_epsilon

    time_vec = np.arange(fs) * dt

    # We need theta, h, and B at each step.  The intermediate gives us coupling
    # (which IS G_i), but we also need the raw ingredients to decompose it.
    # However, the intermediate's "coupling" array is already G_i, computed from
    # B and sin(h_k - theta_i).  We trust that computation (it's the production
    # code's own coupling).  So we can track eps_i = omega_i + coupling_i directly.

    # For decomposition, we need B[i,k] and sin(h_k - theta_i) per edge.
    # B is state.B (NxN symmetric matrix).
    # theta is state.phase (length N).
    # h is the oldest history entry: state.history[0] (a deque).

    rows = []

    for step in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges, eps)

        # Production coupling (already computed by the intermediate)
        coupling_arr = inter["coupling"]  # length N array, G_i for each node

        # Raw ingredients for decomposition
        B_mat = state.B  # NxN symmetric
        theta_arr = state.phase  # length N
        history_list = list(state.history)
        if len(history_list) > 0:
            h_arr = history_list[0]  # oldest history entry, length N
        else:
            h_arr = np.zeros(N)

        # For each K3 node, compute lock error and edge decomposition
        for node_i in [2, 7, 11]:
            omega_i = float(omega_arr[node_i])
            G_i = float(coupling_arr[node_i])
            eps_i = omega_i + G_i

            # Per-edge decomposition
            edge_contribs = {}
            for target_k, edge_idx in NODE_EDGES[node_i]:
                B_ik = float(B_mat[node_i, target_k])
                sin_term = float(np.sin(h_arr[target_k] - theta_arr[node_i]))
                contrib = B_ik * sin_term
                edge_contribs[edge_idx] = {
                    "B_ik": B_ik,
                    "sin_hk_minus_thetai": sin_term,
                    "contrib": contrib,
                }

            # Verify: sum of contributions should equal G_i
            G_reconstructed = sum(v["contrib"] for v in edge_contribs.values())

            row = {
                "step": step,
                "time": time_vec[step],
                "node": node_i,
                "omega_i": omega_i,
                "G_i": G_i,
                "eps_i": eps_i,
                "abs_eps_i": abs(eps_i),
                "G_reconstructed": G_reconstructed,
                "recon_error": abs(G_i - G_reconstructed),
            }
            for edge_idx, ec in edge_contribs.items():
                row[f"B_{edge_idx}"] = ec["B_ik"]
                row[f"sin_{edge_idx}"] = ec["sin_hk_minus_thetai"]
                row[f"contrib_{edge_idx}"] = ec["contrib"]
                row[f"abs_contrib_{edge_idx}"] = abs(ec["contrib"])

            rows.append(row)

        aug.advance_base_state(state, inter)

    df = pd.DataFrame(rows)

    # --- Interval analysis ---
    intervals = [(0,50),(50,100),(100,150),(150,200),(200,250),(250,300),(300,320)]
    int_rows = []
    for node_i in [2, 7, 11]:
        sub = df[df["node"] == node_i]
        for (a,b) in intervals:
            mask = (sub["time"] >= a) & (sub["time"] < b)
            chunk = sub[mask]
            if len(chunk) < 3:
                continue
            t = chunk["time"].values

            # Lock error rate
            eps_fit = fit_log_rate(t, chunk["abs_eps_i"].values, args.signal_floor)

            # Per-edge contribution rates
            edge_fits = {}
            for edge_idx in [25, 29, 59]:
                col = f"abs_contrib_{edge_idx}"
                if col in chunk.columns:
                    edge_fits[edge_idx] = fit_log_rate(
                        t, chunk[col].values, args.signal_floor
                    )

            # B and sin component rates
            B_fits = {}
            sin_fits = {}
            for edge_idx in [25, 29, 59]:
                B_col = f"B_{edge_idx}"
                sin_col = f"sin_{edge_idx}"
                if B_col in chunk.columns:
                    B_fits[edge_idx] = fit_log_rate(
                        t, chunk[B_col].values, args.signal_floor
                    )
                if sin_col in chunk.columns:
                    sin_fits[edge_idx] = fit_log_rate(
                        t, np.abs(chunk[sin_col].values), args.signal_floor
                    )

            # Median values at end of interval for each edge
            for edge_idx in [25, 29, 59]:
                # Only edges incident to this node
                if edge_idx not in [e for _, e in NODE_EDGES[node_i]]:
                    continue
                int_rows.append({
                    "node": node_i,
                    "interval_start": a,
                    "interval_end": b,
                    "edge": edge_idx,
                    "eps_rate": eps_fit["rate"],
                    "eps_R2": eps_fit["R2"],
                    "contrib_rate": edge_fits.get(edge_idx, {}).get("rate", np.nan),
                    "contrib_R2": edge_fits.get(edge_idx, {}).get("R2", np.nan),
                    "B_rate": B_fits.get(edge_idx, {}).get("rate", np.nan),
                    "B_R2": B_fits.get(edge_idx, {}).get("R2", np.nan),
                    "sin_abs_rate": sin_fits.get(edge_idx, {}).get("rate", np.nan),
                    "sin_R2": sin_fits.get(edge_idx, {}).get("R2", np.nan),
                    "final_eps": float(chunk["abs_eps_i"].iloc[-1]),
                    "final_G": float(chunk["G_i"].iloc[-1]),
                    "final_B": float(chunk[f"B_{edge_idx}"].iloc[-1]),
                    "final_sin": float(chunk[f"sin_{edge_idx}"].iloc[-1]),
                    "final_contrib": float(chunk[f"contrib_{edge_idx}"].iloc[-1]),
                    "final_abs_contrib": float(chunk[f"abs_contrib_{edge_idx}"].iloc[-1]),
                })

    idf = pd.DataFrame(int_rows)

    # --- Output ---
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)
    safe_atomic_write_csv(od/"coupling_lock_trajectory.csv", df)
    safe_atomic_write_csv(od/"coupling_lock_intervals.csv", idf)

    # --- Report ---
    lines = [
        "="*70,
        "AIEF-1.4 Coupling-Lock Audit",
        "="*70,
        "",
        f"r_EMA: {r_ema:.6f}   dt: {dt}   alpha: {alpha:.12g}",
        "",
        "Tests:  G_i + omega_i -> 0  for each K3 node (2, 7, 11).",
        "",
        "G_i = sum_k B_{ik} * sin(h_k - theta_i)",
        "",
        "If eps_i = omega_i + G_i decays at r_EMA, the adaptive coupling",
        "compensates the intrinsic frequency with EMA-rate convergence.",
        "",
        "Decomposition per edge shows whether compensation is achieved via:",
        "  - weight adjustment (B_{ik} changing)",
        "  - phase alignment (sin(h_k - theta_i) evolving)",
        "  - both simultaneously",
        "",
        "-"*70,
        "Lock Error |eps_i| = |omega_i + G_i| at Final Step (t=320):",
        "-"*70,
    ]
    for node_i in [2, 7, 11]:
        mask = (df["node"] == node_i) & (df["step"] == fs - 1)
        r = df[mask].iloc[0]
        lines.append(
            f"  node {node_i}:  omega={r['omega_i']:.6f}  "
            f"G={r['G_i']:.6f}  eps={r['eps_i']:.6e}  |eps|={r['abs_eps_i']:.6e}"
        )

    lines.extend([
        "",
        "-"*70,
        "Lock Error Decay Rates by Interval:",
        "-"*70,
        f"  {'Interval':<16} {'node2_rate':>12} {'node7_rate':>12} {'node11_rate':>12}",
        f"  {'-'*16} {'-'*12} {'-'*12} {'-'*12}",
    ])
    for (a,b) in intervals:
        rates = {}
        for node_i in [2, 7, 11]:
            rrow = idf[(idf.node==node_i)&(idf.interval_start==a)&(idf.edge==list(NODE_EDGES[node_i])[0][1])]
            rates[node_i] = rrow["eps_rate"].values[0] if len(rrow)>0 else np.nan
        lines.append(
            f"  [{a:>3},{b:<3})      {rates[2]:>12.6f} {rates[7]:>12.6f} {rates[11]:>12.6f}"
        )

    # Per-edge decomposition for each node (final interval)
    lines.extend([
        "",
        "-"*70,
        "Per-Edge Decomposition, Final Interval [300,320):",
        "-"*70,
    ])
    for node_i in [2, 7, 11]:
        lines.append(f"  Node {node_i} (omega = {omega_arr[node_i]:.6f}):")
        sub = idf[(idf.node==node_i)&(idf.interval_start==300)]
        for _, r in sub.iterrows():
            lines.append(
                f"    Edge {r['edge']}:  B={r['final_B']:.6e}  "
                f"sin={r['final_sin']:.6e}  contrib={r['final_contrib']:.6e}"
            )
            lines.append(
                f"      B_rate={r['B_rate']:.6f}  sin_rate={r['sin_abs_rate']:.6f}  "
                f"contrib_rate={r['contrib_rate']:.6f}"
            )
        lines.append("")

    # Summary: which mechanism?
    lines.extend([
        "-"*70,
        "Mechanism Assessment:",
        "-"*70,
        "",
        "If B_rate ~ 0 and sin_rate ~ 0 for all edges, but contrib_rate ~ 0 and",
        "eps_rate ~ r_EMA:  the compensation is achieved by cancellation BETWEEN",
        "edges (one edge's contribution opposes another's), not by individual",
        "edge-level convergence.  The B and sin terms are individually stationary",
        "but their sum across edges converges.",
        "",
        "If B_rate ~ r_EMA:  the compensation is achieved by weight adjustment.",
        "",
        "If sin_rate ~ r_EMA:  the compensation is achieved by phase alignment.",
        "",
        "If both rates ~ 0 but eps_rate ~ r_EMA across nodes:  the compensation",
        "is a global balance between node-level contributions, not edge-level.",
        "",
        "Evidence class: diagnostic mechanism exploration.",
        "No interpretation is forced.  The numbers speak.",
    ])

    report = "\n".join(lines)
    safe_atomic_write_text(od/"coupling_lock_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 coupling-lock audit",
        "evidence_class": "diagnostic mechanism exploration",
        "seed": args.seed,
        "parameters": {"dt": dt, "r_EMA": r_ema, "alpha": alpha,
                        "scale_epsilon": eps, "signal_floor": args.signal_floor},
        "outputs": ["coupling_lock_trajectory.csv",
                     "coupling_lock_intervals.csv",
                     "coupling_lock_report.txt",
                     "analysis_manifest.json"],
        "tested_hypothesis": "G_i + omega_i -> 0 with EMA-rate convergence",
        "not_a_proof": True,
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")

    print(report)
    print(f"\n[SUCCESS] Artifacts saved to: '{od.resolve()}'")


if __name__ == "__main__":
    main()
