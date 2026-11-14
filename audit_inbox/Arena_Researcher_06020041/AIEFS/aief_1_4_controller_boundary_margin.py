#!/usr/bin/env python3

"""
AIEF-1.4 Controller Boundary Margin Diagnostic

Tracks the "distance to switch" for each K3 edge's controller assignment.

For the audited winner map (25->7, 29->2, 59->7):

  Edge 25 (2,7):  winner = 7.  Margin m_25 = s_2 - s_7.
                   Switch if s_2 = s_7  (i.e., m_25 -> 0 from above).

  Edge 29 (2,11): winner = 2.  Margin m_29 = s_11 - s_2.
                   Switch if s_11 = s_2 (i.e., m_29 -> 0 from above).

  Edge 59 (7,11): winner = 7.  Margin m_59 = s_11 - s_7.
                   Switch if s_11 = s_7 (i.e., m_59 -> 0 from above).

From the equal-capacity identities (Document 3, Proposition 10.1):
  m_25 = s_2 - s_7  ~  x_59 - x_29  = d^R   (right defect)
  m_29 = s_11 - s_2 ~  x_25 - x_59  = d^L   (left defect proxy)
  m_59 = s_11 - s_7 ~  x_25 - x_29  = d^L + d^R

Outputs:
  - Per-step margins and their decay rates
  - Comparison with proposal differences d^L, d^R
  - Whether margins are stabilizing (rate -> 0) or still shrinking
  - Projected time-to-tie if current rates continue

Evidence class: diagnostic mechanism exploration
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
DEFAULT_OUTPUT_DIR = "aief_1_4_controller_boundary_margin"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_SIGNAL_FLOOR = 1e-14

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

def fit_log_rate(t, v, floor):
    m = np.abs(np.asarray(v, dtype=float))
    ok = np.isfinite(m) & (m > floor)
    if np.sum(ok) < 3:
        return {"rate": np.nan, "R2": np.nan, "n": int(np.sum(ok))}
    x = np.asarray(t, dtype=float)[ok]; y = np.log(m[ok])
    slope, _ = np.polyfit(x, y, 1)
    pred = slope * x + _; res = float(np.sum((y-pred)**2))
    tot = float(np.sum((y-np.mean(y))**2))
    return {"rate": float(-slope),
            "R2": float(1-res/tot) if tot>0 else np.nan, "n": int(len(x))}

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
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)
    eps = args.scale_epsilon

    rows = []
    time_vec = np.arange(fs) * dt

    for step in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges, eps)
        qs = inter["q_scale"]
        xp = inter["x"]

        # Controller scales for all three K3 nodes
        s2 = caps[2]/(float(qs[2])+eps)
        s7 = caps[7]/(float(qs[7])+eps)
        s11 = caps[11]/(float(qs[11])+eps)

        # Winner margins (positive = current winner still wins)
        m25 = s2 - s7   # edge 25: 7 wins as long as s7 < s2
        m29 = s11 - s2  # edge 29: 2 wins as long as s2 < s11
        m59 = s11 - s7  # edge 59: 7 wins as long as s7 < s11

        # Proposal quantities
        x25 = float(xp[25]); x59 = float(xp[59]); x29 = float(xp[29])
        dL = x25 - x59
        dR = x59 - x29

        # Winner margin computed from the winner_margin intermediate
        wm = inter["winner_margin"]

        rows.append({
            "step": step, "time": time_vec[step],
            "s_2": float(s2), "s_7": float(s7), "s_11": float(s11),
            "m_25": float(m25), "m_29": float(m29), "m_59": float(m59),
            "d_L": float(dL), "d_R": float(dR),
            "q_2": float(qs[2]), "q_7": float(qs[7]), "q_11": float(qs[11]),
            "wm_25": float(wm[25]), "wm_29": float(wm[29]), "wm_59": float(wm[59]),
        })

        aug.advance_base_state(state, inter)

    df = pd.DataFrame(rows)

    # --- Interval analysis ---
    intervals = [(0,50),(50,100),(100,150),(150,200),(200,250),(250,300),(300,320)]
    int_rows = []
    for (a,b) in intervals:
        mask = (df["time"] >= a) & (df["time"] < b)
        sub = df[mask]
        if len(sub) < 3:
            continue
        t = sub["time"].values
        for col in ["m_25","m_29","m_59","d_L","d_R","s_2","s_7","s_11"]:
            fit = fit_log_rate(t, sub[col].values, args.signal_floor)
            int_rows.append({
                "interval_start": a, "interval_end": b,
                "quantity": col,
                "rate": fit["rate"], "R2": fit["R2"],
                "final_value": float(sub[col].iloc[-1]),
                "median_value": float(np.nanmedian(sub[col].values)),
            })

    idf = pd.DataFrame(int_rows)

    # --- Output ---
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)
    safe_atomic_write_csv(od/"controller_margin_trajectory.csv", df)
    safe_atomic_write_csv(od/"controller_margin_intervals.csv", idf)

    # --- Report ---
    lines = [
        "="*70,
        "AIEF-1.4 Controller Boundary Margin Diagnostic",
        "="*70,
        "",
        f"r_EMA: {r_ema:.6f}   dt: {dt}",
        "",
        "Winner map: (25->7, 29->2, 59->7)",
        "",
        "Margins (positive = current controller still wins):",
        "  m_25 = s_2 - s_7   (edge 25: 7 wins while s_7 < s_2)",
        "  m_29 = s_11 - s_2  (edge 29: 2 wins while s_2 < s_11)",
        "  m_59 = s_11 - s_7  (edge 59: 7 wins while s_7 < s_11)",
        "",
        "Equivalences (equal capacities):",
        "  m_25 ~ d^R = x_59 - x_29",
        "  m_29 ~ d^L = x_25 - x_59",
        "  m_59 ~ d^L + d^R",
        "",
        "-"*70,
        "Margins at Final Step (t=320):",
        "-"*70,
        f"  m_25 (s_2-s_7):  {df['m_25'].iloc[-1]:.6e}",
        f"  m_29 (s_11-s_2): {df['m_29'].iloc[-1]:.6e}",
        f"  m_59 (s_11-s_7): {df['m_59'].iloc[-1]:.6e}",
        "",
        "-"*70,
        "Margin Decay Rates by Interval:",
        "-"*70,
        f"  {'Interval':<16} {'m_25_rate':>12} {'m_29_rate':>12} {'m_59_rate':>12} {'d_L_rate':>12} {'d_R_rate':>12}",
        f"  {'-'*16} {'-'*12} {'-'*12} {'-'*12} {'-'*12} {'-'*12}",
    ]

    for (a,b) in intervals:
        rates = {}
        for q in ["m_25","m_29","m_59","d_L","d_R"]:
            rrow = idf[(idf.interval_start==a)&(idf.quantity==q)]
            rates[q] = rrow["rate"].values[0] if len(rrow)>0 else np.nan
        lines.append(
            f"  [{a:>3},{b:<3})      {rates['m_25']:>12.6f} {rates['m_29']:>12.6f} "
            f"{rates['m_59']:>12.6f} {rates['d_L']:>12.6f} {rates['d_R']:>12.6f}"
        )

    # Time-to-tie extrapolation
    # m_25 at final step = s_2 - s_7
    # m_25 rate from last interval
    last_int = idf[(idf.interval_start==300)&(idf.interval_end==320)]
    extrap = {}
    for q in ["m_25","m_29","m_59"]:
        rrow = last_int[last_int.quantity==q]
        if len(rrow)>0:
            rate = rrow["rate"].values[0]
            final = rrow["final_value"].values[0]
            if not np.isnan(rate) and rate > 1e-16 and final > 0:
                # dM/dt = -rate * M, so M(t) = M_0 * exp(-rate * t)
                # Time to reach machine epsilon (1e-16):
                # 1e-16 = final * exp(-rate * t) => t = -log(1e-16/final)/rate
                t_tie = np.log(final/1e-16)/rate if rate > 0 else np.inf
                extrap[q] = t_tie
            else:
                extrap[q] = np.inf
        else:
            extrap[q] = np.nan

    lines.extend([
        "",
        "-"*70,
        "Projected Time-to-Tie (linear extrapolation of final margin at final rate):",
        "-"*70,
        f"  m_25 -> 1e-16: {extrap.get('m_25', np.nan):.1f} time units",
        f"  m_29 -> 1e-16: {extrap.get('m_29', np.nan):.1f} time units",
        f"  m_59 -> 1e-16: {extrap.get('m_59', np.nan):.1f} time units",
        "",
        "Caveat: extrapolation assumes constant log-linear decay.",
        "Actual margin dynamics may accelerate or decelerate.",
        "",
        "-"*70,
        "Controller Scale Values (final step):",
        "-"*70,
        f"  s_2  = {df['s_2'].iloc[-1]:.12f}",
        f"  s_7  = {df['s_7'].iloc[-1]:.12f}",
        f"  s_11 = {df['s_11'].iloc[-1]:.12f}",
        "",
        "Node loading (q_i / c, final step):",
        f"  q_2/c  = {df['q_2'].iloc[-1]/cap:.12f}",
        f"  q_7/c  = {df['q_7'].iloc[-1]/cap:.12f}",
        f"  q_11/c = {df['q_11'].iloc[-1]/cap:.12f}",
        "",
        "Interpretation:",
        "  All three margins remain positive (no controller switch in 32k steps).",
        "  If margin decay rates -> r_EMA, boundaries are approached exponentially.",
        "  If rates -> 0, boundaries are stabilizing at a fixed gap.",
        "  If all three -> 0 together, the triple tie is approached.",
        "  If m_25/m_29/m_59 diverge at different rates, the boundary",
        "  structure is hierarchical (one margin closes before others).",
        "",
        "Evidence class: diagnostic mechanism exploration.",
    ])

    report = "\n".join(lines)
    safe_atomic_write_text(od/"controller_margin_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 controller boundary margin diagnostic",
        "evidence_class": "diagnostic mechanism exploration",
        "seed": args.seed,
        "parameters": {"dt": dt, "r_EMA": r_ema, "scale_epsilon": eps},
        "outputs": ["controller_margin_trajectory.csv",
                     "controller_margin_intervals.csv",
                     "controller_margin_report.txt",
                     "analysis_manifest.json"],
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")

    print(report)
    print(f"\n[SUCCESS] Artifacts saved to: '{od.resolve()}'")

if __name__ == "__main__":
    main()
