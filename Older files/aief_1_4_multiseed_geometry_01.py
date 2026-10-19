#!/usr/bin/env python3

"""
AIEF-1.4 Multi-Seed Slow Bundle Geometry

Scans all seeds in the frozen run, identifies K3 structure, and
runs the slow-bundle geometry diagnostics on seeds sharing the
exceptional (7,2,7) winner map.

For each seed:
  1. Replay to final step
  2. Check K3 edge activity and winner map
  3. If (7,2,7): build Jacobian, compute slow subspace geometry
  4. Tabulate: principal angles, Frobenius norms, compressed
     operator scalar fraction, normality, off-diagonal ratio,
     mu_phase, slow dimension

Outputs a single CSV comparing all seeds.
"""

from __future__ import annotations

import argparse, hashlib, json, math, os, sys, tempfile, time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import linalg as la

DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_multiseed_geometry"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_PERTURBATION = 1e-8
MAX_SEEDS = 40

K3_NODES = [2, 7, 11]
K3_EDGE_LIST = [(2,7,25), (2,11,29), (7,11,59)]
DIRECTED_PAIRS = [(2,7),(7,2),(2,11),(11,2),(7,11),(11,7)]

def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as h:
        while b := h.read(1024*1024): d.update(b)
    return d.hexdigest()

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

# ── state I/O ──
def snapshot_state(state):
    hl = list(state.history)
    return {"B": state.B.copy(), "coherence_acc": state.coherence_acc.copy(),
            "history": [e.copy() for e in hl]}

def restore_state(state, snap):
    state.B[:] = snap["B"]
    state.coherence_acc[:] = snap["coherence_acc"]
    state.history.clear()
    for e in snap["history"]: state.history.append(e)

def extract_fundamental(state):
    hl = list(state.history)
    ho = hl[0] if hl else np.zeros(len(state.B))
    Bm, Cm = state.B, state.coherence_acc
    v = [float(ho[i]) for i in K3_NODES]
    for _,_,e in K3_EDGE_LIST:
        ia,ib = (2,7) if e==25 else ((2,11) if e==29 else (7,11))
        v.append(float(Bm[ia,ib]))
    for ia,ib in DIRECTED_PAIRS:
        c = Cm[ia,ib]; v.append(float(c.real)); v.append(float(c.imag))
    return np.array(v, dtype=float)

def inject_fundamental(state, vec):
    vec = np.asarray(vec, dtype=float)
    Bm, Cm = state.B, state.coherence_acc
    idx = 0
    ho = {i: float(vec[idx+i2]) for i2,i in enumerate(K3_NODES)}; idx += 3
    hl = list(state.history)
    if hl:
        oldest = hl[0].copy()
        for i in K3_NODES: oldest[i] = ho[i]
        hl[0] = oldest; state.history.clear()
        for e in hl: state.history.append(e)
    for _,_,e in K3_EDGE_LIST:
        ia,ib = (2,7) if e==25 else ((2,11) if e==29 else (7,11))
        Bm[ia,ib] = Bm[ib,ia] = float(vec[idx]); idx += 1
    for ia,ib in DIRECTED_PAIRS:
        Cm[ia,ib] = complex(float(vec[idx]), float(vec[idx+1])); idx += 2

def build_real_slow_basis(evecs_complex, slow_idx, tol=1e-12):
    real_basis = []
    used = set()
    for i in slow_idx:
        if i in used: continue
        v = evecs_complex[:, i]
        if abs(v.imag).max() < tol:
            real_basis.append(np.asarray(v.real, dtype=float).copy())
            used.add(i)
        else:
            partner = None
            for j in slow_idx:
                if j == i or j in used: continue
                w = evecs_complex[:, j]
                if np.allclose(v.real, w.real, atol=tol) and \
                   np.allclose(v.imag, -w.imag, atol=tol):
                    partner = j; break
            real_basis.append(np.asarray(v.real, dtype=float).copy())
            real_basis.append(np.asarray(v.imag, dtype=float).copy())
            used.add(i)
            if partner is not None: used.add(partner)
    if not real_basis: return np.zeros((evecs_complex.shape[0], 0), dtype=float)
    Q, _ = np.linalg.qr(np.column_stack(real_basis))
    return Q

# ── single-seed geometry (compact, returns dict) ──
def analyze_seed_geometry(state, base, aug, model, caps, A, edges_mat,
                          eps_sc, pert, r_ema, dt, fs, seed_id):
    """Full geometry analysis for one seed.  Returns dict or None on failure."""
    n_vars = 18

    # Snap at final step
    snap_fs = snapshot_state(state)
    inter_fs = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    aug.advance_base_state(state, inter_fs)
    v_after = extract_fundamental(state)

    # Build Jacobian
    J = np.zeros((n_vars, n_vars))
    for col in range(n_vars):
        restore_state(state, snap_fs)
        vc = extract_fundamental(state)
        delta = pert * max(1.0, abs(vc[col]))
        vc[col] += delta
        inject_fundamental(state, vc)
        inter_p = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter_p)
        vp = extract_fundamental(state)
        J[:, col] = (vp - v_after) / delta

    # Eigendecomposition
    evals, evecs_r = np.linalg.eig(J)
    abs_evals = np.abs(evals)
    rates = -np.log(np.maximum(abs_evals, 1e-300)) / dt
    slow_mask = (rates > r_ema*0.99) & (rates < r_ema*1.01) & (abs_evals < 1.0)
    slow_idx = np.where(slow_mask)[0]
    n_slow = len(slow_idx)
    if n_slow == 0:
        return {"seed": seed_id, "n_slow": 0, "error": "no slow EMA-cluster modes"}

    Q_slow = build_real_slow_basis(evecs_r, slow_idx)
    d = Q_slow.shape[1]
    if d == 0:
        return {"seed": seed_id, "n_slow": 0, "error": "real slow basis empty"}

    # Compressed operator
    T = Q_slow.T @ J @ Q_slow
    diag = np.diag(np.diag(T))
    offdiag = T - diag
    diag_norm = float(np.linalg.norm(diag, 'fro'))
    off_norm  = float(np.linalg.norm(offdiag, 'fro'))
    total_norm = float(np.linalg.norm(T, 'fro'))
    ratio_offdiag = off_norm / (diag_norm + 1e-30)

    mean_diag = float(np.mean(np.diag(T)))
    scalar_part = mean_diag * np.eye(d)
    dev_from_scalar = float(np.linalg.norm(T - scalar_part, 'fro'))
    frac_scalar = 1.0 - dev_from_scalar / (total_norm + 1e-30)

    nonnorm = float(np.linalg.norm(T @ T.T - T.T @ T, 'fro'))
    norm_T = float(np.linalg.norm(T, 'fro'))
    nonnorm_ratio = nonnorm / (norm_T**2 + 1e-30)

    Schur_T, _ = la.schur(T)
    S_lower = np.tril(Schur_T, -1)
    S_diag  = np.diag(np.diag(Schur_T))
    S_upper = np.triu(Schur_T, 1)
    quasi_tri = float(np.linalg.norm(S_lower, 'fro')) / \
                (float(np.linalg.norm(S_diag,'fro')) + float(np.linalg.norm(S_upper,'fro')) + 1e-30)

    # Principal angles vs C
    C_basis = np.zeros((n_vars, 12))
    C_basis[6:18, :] = np.eye(12)
    _, S_pa, _ = np.linalg.svd(Q_slow.T @ C_basis, full_matrices=False)
    angles = np.arccos(np.clip(S_pa, 0.0, 1.0))
    max_angle_deg = float(np.max(angles)) * 180.0 / np.pi

    # Frobenius projection norms
    proj_h2 = float(np.sum(Q_slow[0:3, :]**2))
    proj_B2 = float(np.sum(Q_slow[3:6, :]**2))
    proj_C2 = float(np.sum(Q_slow[6:18, :]**2))
    total2  = proj_h2 + proj_B2 + proj_C2
    frac_h = proj_h2 / (total2 + 1e-30)
    frac_B = proj_B2 / (total2 + 1e-30)
    frac_C = proj_C2 / (total2 + 1e-30)

    # Phase Jacobian eigenvalues (same method as transverse script)
    # Build W matrix
    h_arr = list(state.history)[0] if len(list(state.history)) > 0 else np.zeros(len(state.B))
    pf = inter_fs["phase_factor"]
    omega_model = np.asarray(model["omega"], dtype=float)
    tau_delay = 0.5
    theta = np.zeros(len(omega_model))
    for node_i, partner in [(2,7),(7,2),(11,2)]:
        const_ik = 0.5*(omega_model[node_i]+omega_model[partner])*tau_delay
        theta[node_i] = float(np.angle(pf[node_i,partner])+h_arr[partner]+const_ik)
    B_mat = state.B
    idx_map = {2:0, 7:1, 11:2}
    W = np.zeros((3,3))
    for ia, ib, _ in K3_EDGE_LIST:
        i, j = idx_map[ia], idx_map[ib]
        w_ij = float(B_mat[ia,ib]) * math.cos(h_arr[ib]-theta[ia])
        w_ji = float(B_mat[ib,ia]) * math.cos(h_arr[ia]-theta[ib])
        W[i,j] = w_ij; W[j,i] = w_ji
    L_W = np.diag(np.sum(W, axis=1)) - W
    J_phase = -L_W
    ev_phase = np.linalg.eigvals(J_phase)
    mu_phase = float(-max(ev_phase.real[1:]))  # skip common mode

    # Compressed eigenvalue rates
    ev_T = np.linalg.eigvals(T)
    rates_T = -np.log(np.maximum(np.abs(ev_T), 1e-300)) / dt
    mean_rate = float(np.mean(rates_T))
    std_rate  = float(np.std(rates_T))

    return {
        "seed": seed_id,
        "n_slow": n_slow,
        "slow_dim": d,
        "ratio_offdiag": ratio_offdiag,
        "frac_scalar": frac_scalar,
        "nonnorm_ratio": nonnorm_ratio,
        "quasi_tri": quasi_tri,
        "max_angle_deg": max_angle_deg,
        "frac_h": frac_h,
        "frac_B": frac_B,
        "frac_C": frac_C,
        "mu_phase": mu_phase,
        "mean_diag_T": mean_diag,
        "mean_rate_T": mean_rate,
        "std_rate_T": std_rate,
        "r_ema": r_ema,
    }

# ── K3 structure scan ──
def scan_k3_structure(state, base, aug, model, caps, A, edges_mat, eps_sc, fs):
    """Replay to final step and report K3 edge activity and winner map."""
    for _ in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter)
    inter_final = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    winners = inter_final["winner_code"]
    B_mat = state.B
    B_c = model.get("B_c", 0.12) if isinstance(model, dict) else 0.12
    try:
        B_c = float(model["B_c"])
    except:
        B_c = 0.12

    info = {}
    for ia, ib, e in K3_EDGE_LIST:
        active = bool(B_mat[ia, ib] > B_c)
        winner = int(winners[e])
        info[f"edge_{e}_active"] = active
        info[f"edge_{e}_winner"] = winner if active else -1
    info["winner_map"] = (
        f"({info['edge_25_winner']},{info['edge_29_winner']},{info['edge_59_winner']})"
    )
    info["is_727"] = (
        info.get("edge_25_winner") == 7 and
        info.get("edge_29_winner") == 2 and
        info.get("edge_59_winner") == 7
    )
    return info

# ── CLI ──
def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--npz", default=DEFAULT_NPZ)
    p.add_argument("--manifest", default=DEFAULT_MANIFEST)
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--dt", type=float, default=DEFAULT_DT)
    p.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON)
    p.add_argument("--perturbation", type=float, default=DEFAULT_PERTURBATION)
    p.add_argument("--max-seeds", type=int, default=MAX_SEEDS)
    return p.parse_args()

def main():
    args = parse_args()
    for p in (args.npz, args.manifest):
        if not os.path.isfile(p): raise FileNotFoundError(f"Missing: {p}")

    base, ca, aug = load_production_modules()
    with open(args.manifest) as h: manifest = json.load(h)
    model = manifest["model"]
    dt = float(model["dt"])
    alpha = math.exp(-dt/float(model["T_window"]))
    r_ema = -np.log(alpha)/dt
    cap = (float(model["a"])-float(model["delta"]))/float(model["q"])
    caps = np.full(int(model["N"]), cap)
    N = int(model["N"])
    A, edges_mat = base.incidence_matrix(N)
    fs = int(manifest["protocol"]["future_steps"])
    eps_sc, pert = args.scale_epsilon, args.perturbation

    # ── Discover seeds ──
    with np.load(args.npz, allow_pickle=False) as data:
        all_keys = list(data.keys())
    seed_keys = sorted(set(
        k.split("/")[0] for k in all_keys
        if "continue" in k and "B_final" in k
    ))
    n_available = len(seed_keys)
    n_seeds = min(n_available, args.max_seeds)
    print(f"Found {n_available} seeds in npz.  Will scan up to {n_seeds}.")

    # Pass 1: K3 structure scan
    print("\n--- Pass 1: K3 structure scan ---")
    k3_rows = []
    for si, seed_id in enumerate(seed_keys[:n_seeds]):
        with np.load(args.npz, allow_pickle=False) as data:
            state = base.load_split_state(data, seed_id)
        info = scan_k3_structure(state, base, aug, model, caps, A, edges_mat, eps_sc, fs)
        info["seed"] = seed_id
        k3_rows.append(info)
        print(f"  [{si+1:>2}/{n_seeds}] seed {seed_id}: {info['winner_map']}  "
              f"727={info['is_727']}")
    k3_df = pd.DataFrame(k3_rows)
    n_727 = int(k3_df["is_727"].sum()) if "is_727" in k3_df.columns else 0
    print(f"\n  Seeds with (7,2,7) winner map: {n_727}/{n_seeds}")

    # Pass 2: Full geometry on (7,2,7) seeds
    print(f"\n--- Pass 2: Full geometry on (7,2,7) seeds ---")
    geo_rows = []
    seeds_727 = k3_df[k3_df["is_727"]]["seed"].tolist()
    for si, seed_id in enumerate(seeds_727):
        t0 = time.time()
        with np.load(args.npz, allow_pickle=False) as data:
            state = base.load_split_state(data, seed_id)
        for _ in range(fs):
            inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
            aug.advance_base_state(state, inter)
        result = analyze_seed_geometry(state, base, aug, model, caps, A, edges_mat,
                                        eps_sc, pert, r_ema, dt, fs, seed_id)
        elapsed = time.time() - t0
        if result:
            geo_rows.append(result)
            print(f"  [{si+1:>2}/{len(seeds_727)}] seed {seed_id}: "
                  f"d={result.get('slow_dim','?')} "
                  f"mu_phase={result.get('mu_phase',np.nan):.4f} "
                  f"frac_C={result.get('frac_C',0):.6f} "
                  f"scalar={result.get('frac_scalar',0):.4f} "
                  f"({elapsed:.0f}s)")
        else:
            print(f"  [{si+1:>2}/{len(seeds_727)}] seed {seed_id}: FAILED")
    geo_df = pd.DataFrame(geo_rows)

    # ── Output ──
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)
    safe_atomic_write_csv(od/"k3_structure_scan.csv", k3_df)
    if len(geo_df) > 0:
        safe_atomic_write_csv(od/"multiseed_geometry.csv", geo_df)

    # ── Report ──
    lines = [
        "="*70,
        "AIEF-1.4 Multi-Seed Slow Bundle Geometry",
        "="*70,
        f"Seeds scanned: {n_seeds}",
        f"Seeds with (7,2,7) winner map: {n_727}",
        f"Full geometry computed on: {len(geo_df)} seeds",
        f"r_EMA: {r_ema:.6f}   alpha: {alpha:.12g}   dt: {dt}",
        "",
        "─"*70,
        "K3 Winner Map Distribution:",
        "─"*70,
    ]
    if "winner_map" in k3_df.columns:
        wm_counts = k3_df["winner_map"].value_counts()
        for wm, count in wm_counts.items():
            lines.append(f"  {wm}: {count} seeds")
    lines.append("")

    if len(geo_df) > 0:
        lines.extend([
            "─"*70,
            "Geometry Diagnostics Across (7,2,7) Seeds:",
            "─"*70,
            f"  {'Metric':<30} {'min':>12} {'median':>12} {'max':>12}",
            f"  {'-'*30} {'-'*12} {'-'*12} {'-'*12}",
        ])
        for col, label in [
            ("slow_dim", "Slow subspace dimension"),
            ("mu_phase", "mu_phase"),
            ("max_angle_deg", "Max principal angle (°)"),
            ("frac_C", "C Frobenius fraction"),
            ("frac_B", "B Frobenius fraction"),
            ("frac_h", "h Frobenius fraction"),
            ("frac_scalar", "Scalar fraction"),
            ("ratio_offdiag", "Off-diag / diag ratio"),
            ("nonnorm_ratio", "Non-normality ratio"),
            ("mean_rate_T", "Mean compressed rate"),
            ("std_rate_T", "Std compressed rate"),
        ]:
            if col in geo_df.columns:
                vals = geo_df[col].dropna()
                if len(vals) > 0:
                    lines.append(
                        f"  {label:<30} {vals.min():>12.4e} {vals.median():>12.4e} "
                        f"{vals.max():>12.4e}"
                    )
        lines.extend([
            "",
            "─"*70,
            "Per-Seed Detail:",
            "─"*70,
            f"  {'seed':<24} {'d':>3} {'mu_ph':>8} {'ang°':>8} "
            f"{'frac_C':>10} {'scalar':>8} {'offdiag':>10} {'nonnorm':>10}",
            f"  {'-'*24} {'-'*3} {'-'*8} {'-'*8} {'-'*10} {'-'*8} {'-'*10} {'-'*10}",
        ])
        for _, r in geo_df.iterrows():
            lines.append(
                f"  {str(r['seed']):<24} {int(r['slow_dim']):>3} "
                f"{r['mu_phase']:>8.4f} {r['max_angle_deg']:>8.4f} "
                f"{r['frac_C']:>10.6f} {r['frac_scalar']:>8.4f} "
                f"{r['ratio_offdiag']:>10.2e} {r['nonnorm_ratio']:>10.2e}"
            )

        # Interpretation
        if len(geo_df) >= 2:
            c_std = float(geo_df["frac_C"].std())
            mu_std = float(geo_df["mu_phase"].std())
            scalar_std = float(geo_df["frac_scalar"].std())
            lines.extend([
                "",
                "─"*70,
                "Cross-Seed Variability:",
                "─"*70,
                f"  std(frac_C)     = {c_std:.2e}",
                f"  std(mu_phase)   = {mu_std:.4f}",
                f"  std(scalar_frac)= {scalar_std:.2e}",
                "",
            ])
            if c_std < 1e-4 and mu_std < 0.01 and scalar_std < 1e-4:
                lines.append("  → All diagnostics are tightly clustered across seeds.")
                lines.append("    The slow bundle geometry is a robust property of the")
                lines.append("    (7,2,7) attractor, not a single-seed quirk.")
            elif c_std < 1e-2:
                lines.append("  → Diagnostics show moderate cross-seed variation.")
                lines.append("    The qualitative structure persists but quantitative")
                lines.append("    details vary.")
            else:
                lines.append("  → Substantial cross-seed variation detected.")
                lines.append("    The exceptional seed may not be representative.")
    else:
        lines.append("  No (7,2,7) seeds found.  Cannot report geometry.")

    report = "\n".join(lines)
    safe_atomic_write_text(od/"multiseed_geometry_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 multi-seed slow bundle geometry",
        "n_seeds_scanned": n_seeds,
        "n_727_seeds": n_727,
        "n_geometry_computed": len(geo_df),
        "parameters": {"dt":dt, "r_EMA":r_ema, "alpha":alpha, "perturbation":pert},
        "outputs": ["k3_structure_scan.csv", "multiseed_geometry.csv",
                     "multiseed_geometry_report.txt", "analysis_manifest.json"],
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")
    print(report)
    print(f"\nDone. → {od.resolve()}")

if __name__ == "__main__":
    main()
