#!/usr/bin/env python3

"""
AIEF-1.4 Multi-Seed Slow Bundle Geometry (v2)

Robustness test across all seeds in the frozen run.

Pass 1 — K3 structure scan (all seeds, fast).
Pass 2 — Full geometry on (7,2,7) seeds (expensive).

Key improvements over v1:
  - Spectral clustering for slow-mode identification (not fixed ±1% band)
  - Cross-seed subspace comparison via principal angles
  - Average projector across seeds
  - Numerical sensitivity check (Jacobian at 3 perturbation levels)
  - Explicit survivorship reporting

Outputs:
  k3_structure_scan.csv
  multiseed_geometry.csv
  cross_seed_angles.csv
  average_projector_eigenvalues.csv
  sensitivity_check.csv
  multiseed_geometry_report.txt
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
DEFAULT_MAX_SEEDS = 40

K3_NODES = [2, 7, 11]
K3_EDGE_LIST = [(2,7,25), (2,11,29), (7,11,59)]
DIRECTED_PAIRS = [(2,7),(7,2),(2,11),(11,2),(7,11),(11,7)]

# ── utilities ──────────────────────────────────────────────────────
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

# ── state I/O ───────────────────────────────────────────────────────
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

# ── spectral clustering: find slow cluster via largest gap ──────────
def identify_slow_cluster(rates, abs_evals, dt, min_cluster=3):
    """
    Find the slowest eigenvalue cluster via the largest spectral gap.

    Returns (slow_idx, slow_rate_low, slow_rate_high) or (None,*,*) if
    no cluster with >= min_cluster eigenvalues found below rate 1.0.
    """
    # Sort by rate ascending (slowest first)
    order = np.argsort(rates)
    sorted_rates = rates[order]
    sorted_abs   = abs_evals[order]

    # Only consider contracting modes (|λ| < 1) with positive rate
    valid = (sorted_abs < 1.0) & (sorted_rates > 0)
    if np.sum(valid) < min_cluster:
        return None, np.nan, np.nan

    valid_rates = sorted_rates[valid]
    valid_order = order[valid]

    # Find largest gap between consecutive rates
    if len(valid_rates) < 2:
        return None, np.nan, np.nan

    gaps = np.diff(valid_rates)
    # Also consider gap from 0 to first rate
    gaps_with_boundary = np.concatenate([[valid_rates[0]], gaps])

    # The slow cluster is everything below the largest gap
    max_gap_idx = np.argmax(gaps_with_boundary)

    if max_gap_idx == 0:
        # Largest gap is from 0 to first rate — no slow cluster
        return None, np.nan, np.nan

    # slow cluster indices in valid_rates: 0 .. max_gap_idx-1
    n_in_cluster = max_gap_idx
    if n_in_cluster < min_cluster:
        return None, np.nan, np.nan

    cluster_order_idx = valid_order[:n_in_cluster]
    cluster_rates = sorted_rates[:max_gap_idx]  # corresponds to order[:max_gap_idx]

    return (cluster_order_idx,
            float(np.min(cluster_rates)), float(np.max(cluster_rates)))

# ── real slow basis ─────────────────────────────────────────────────
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

# ── full geometry for one seed ──────────────────────────────────────
def build_jacobian(state, snap_fs, aug, model, caps, A, edges_mat, eps_sc,
                   pert, n_vars, v_after):
    """Build 18×18 Jacobian at given perturbation level."""
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
    return J

def analyze_seed_geometry(state, base, aug, model, caps, A, edges_mat,
                          eps_sc, pert, r_ema, dt, fs, seed_id):
    """Full geometry analysis.  Returns (dict, Q_slow) or (None, None)."""
    n_vars = 18

    snap_fs = snapshot_state(state)
    inter_fs = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    aug.advance_base_state(state, inter_fs)
    v_after = extract_fundamental(state)

    J = build_jacobian(state, snap_fs, aug, model, caps, A, edges_mat, eps_sc,
                       pert, n_vars, v_after)

    evals, evecs_r = np.linalg.eig(J)
    abs_evals = np.abs(evals)
    rates = -np.log(np.maximum(abs_evals, 1e-300)) / dt

    slow_idx, rate_low, rate_high = identify_slow_cluster(rates, abs_evals, dt)
    # Compute largest gap for reporting
    all_rates_sorted = sorted(rates[abs_evals < 1.0])
    gaps = np.diff(all_rates_sorted) if len(all_rates_sorted) > 1 else []
    largest_gap = float(max(gaps)) if len(gaps) > 0 else np.nan

    if slow_idx is None:
        return ({"seed": seed_id, "n_slow": 0,
                  "error": "no slow cluster identified",
                  "rate_low": rate_low, "rate_high": rate_high,
                  "largest_gap": largest_gap,
                  "full_spectrum_top12": [float(x) for x in all_rates_sorted[:12]],
                  "n_total_contracting": len(all_rates_sorted)}, None)

    n_slow = len(slow_idx)
    Q_slow = build_real_slow_basis(evecs_r, slow_idx)
    d = Q_slow.shape[1]
    if d == 0:
        return ({"seed": seed_id, "n_slow": 0, "error": "real basis empty"}, None)

    T = Q_slow.T @ J @ Q_slow
    diag = np.diag(np.diag(T))
    offdiag = T - diag
    diag_norm = float(np.linalg.norm(diag, 'fro'))
    off_norm  = float(np.linalg.norm(offdiag, 'fro'))
    total_norm = float(np.linalg.norm(T, 'fro'))

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
                (float(np.linalg.norm(S_diag,'fro')) +
                 float(np.linalg.norm(S_upper,'fro')) + 1e-30)

    # Principal angles vs C
    C_basis = np.zeros((n_vars, 12)); C_basis[6:18, :] = np.eye(12)
    _, S_pa, _ = np.linalg.svd(Q_slow.T @ C_basis, full_matrices=False)
    angles = np.arccos(np.clip(S_pa, 0.0, 1.0))

    # Frobenius norms
    proj_h2 = float(np.sum(Q_slow[0:3, :]**2))
    proj_B2 = float(np.sum(Q_slow[3:6, :]**2))
    proj_C2 = float(np.sum(Q_slow[6:18, :]**2))
    total2  = proj_h2 + proj_B2 + proj_C2

    # Phase Jacobian
    h_arr = list(state.history)[0] if len(list(state.history)) > 0 \
            else np.zeros(len(state.B))
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
    mu_phase = float(-max(ev_phase.real[1:]))

    ev_T = np.linalg.eigvals(T)
    rates_T = -np.log(np.maximum(np.abs(ev_T), 1e-300)) / dt

    # Eigenvalue variance (primary metric for scalar-ness; see also frac_scalar)
    lambda_var = float(np.var(np.abs(ev_T)))

    # Condition number of eigenvector matrix
    try:
        _, s, _ = np.linalg.svd(evecs_r[:, slow_idx], full_matrices=False)
        cond_num = float(s[0] / (s[-1] + 1e-30)) if len(s) > 0 else np.nan
    except:
        cond_num = np.nan

    # Store full spectrum for later inspection
    all_rates_sorted2 = sorted(rates[abs_evals < 1.0])

    result = {
        "seed": seed_id,
        "n_slow": n_slow,
        "slow_dim": d,
        "rate_low": rate_low,
        "rate_high": rate_high,
        "n_total_contracting": len(all_rates_sorted2),
        "largest_gap": largest_gap,
        "full_spectrum_top12": [float(x) for x in all_rates_sorted2[:12]],
        "ratio_offdiag": off_norm / (diag_norm + 1e-30),
        "frac_scalar": frac_scalar,
        "lambda_variance": lambda_var,
        "cond_num": cond_num,
        "nonnorm_ratio": nonnorm_ratio,
        "quasi_tri": quasi_tri,
        "max_angle_deg": float(np.max(angles)) * 180.0 / np.pi,
        "frac_h": proj_h2 / (total2 + 1e-30),
        "frac_B": proj_B2 / (total2 + 1e-30),
        "frac_C": proj_C2 / (total2 + 1e-30),
        "mu_phase": mu_phase,
        "mean_diag_T": mean_diag,
        "mean_rate_T": float(np.mean(rates_T)),
        "std_rate_T": float(np.std(rates_T)),
        "r_ema": r_ema,
    }
    return result, Q_slow

# ── K3 structure scan ───────────────────────────────────────────────
def scan_k3_structure(state, base, aug, model, caps, A, edges_mat, eps_sc, fs):
    for _ in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter)
    inter_final = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    winners = inter_final["winner_code"]
    B_mat = state.B
    try: B_c = float(model["B_c"])
    except: B_c = 0.12
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

# ── CLI ─────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--npz", default=DEFAULT_NPZ)
    p.add_argument("--manifest", default=DEFAULT_MANIFEST)
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--dt", type=float, default=DEFAULT_DT)
    p.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON)
    p.add_argument("--perturbation", type=float, default=DEFAULT_PERTURBATION)
    p.add_argument("--max-seeds", type=int, default=DEFAULT_MAX_SEEDS)
    p.add_argument("--sensitivity-seeds", type=int, default=3,
                   help="Number of (7,2,7) seeds to run sensitivity check on")
    return p.parse_args()

# ── main ────────────────────────────────────────────────────────────
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

    # ── Discover seeds from consolidated NPZ ──
    # Keys follow pattern:  continue/seed_XXXX/...
    # Extract just the numeric seed ID.
    run_dir = Path(args.npz).parent
    with np.load(args.npz, allow_pickle=False) as data:
        all_keys = list(data.keys())
    seed_keys = sorted(set(
        k.split("/")[1].replace("seed_", "")
        for k in all_keys
        if k.startswith("continue/seed_") and "/B_final" in k
    ))
    n_available = len(seed_keys)
    n_seeds = min(n_available, args.max_seeds)
    print(f"Found {n_available} seeds.  Scanning up to {n_seeds}.")

    # ------ Pass 1: K3 structure scan ------
    print("\n--- Pass 1: K3 structure scan ---")
    k3_rows = []
    for si, seed_id in enumerate(seed_keys[:n_seeds]):
        try:
            with np.load(args.npz, allow_pickle=False) as data:
                state = base.load_split_state(data, seed_id)
            info = scan_k3_structure(state, base, aug, model, caps, A,
                                      edges_mat, eps_sc, fs)
            info["seed"] = seed_id
            k3_rows.append(info)
            print(f"  [{si+1:>2}/{n_seeds}] {seed_id}: {info['winner_map']}  "
                  f"727={info['is_727']}")
        except Exception as e:
            print(f"  [{si+1:>2}/{n_seeds}] {seed_id}: FAILED — {e}")
            # Add a placeholder row so the seed is tracked
            k3_rows.append({"seed": seed_id, "winner_map": "ERROR",
                            "is_727": False,
                            "edge_25_active": False, "edge_25_winner": -1,
                            "edge_29_active": False, "edge_29_winner": -1,
                            "edge_59_active": False, "edge_59_winner": -1})
    k3_df = pd.DataFrame(k3_rows)
    if len(k3_df) == 0 or "is_727" not in k3_df.columns:
        n_727 = 0
    else:
        n_727 = int(k3_df["is_727"].sum())
    print(f"\n  (7,2,7) seeds: {n_727}/{n_seeds}")

    # ------ Pass 2: Full geometry ------
    print(f"\n--- Pass 2: Full geometry on (7,2,7) seeds ---")
    if n_727 == 0:
        seeds_727 = []
    else:
        seeds_727 = k3_df.loc[k3_df["is_727"], "seed"].tolist()
    geo_rows = []
    Q_list = []       # store slow bases for cross-seed comparison
    seed_list = []    # corresponding seed IDs

    for si, seed_id in enumerate(seeds_727):
        t0 = time.time()
        with np.load(args.npz, allow_pickle=False) as data:
            state = base.load_split_state(data, seed_id)
        for _ in range(fs):
            inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
            aug.advance_base_state(state, inter)
        result, Q_slow = analyze_seed_geometry(
            state, base, aug, model, caps, A, edges_mat, eps_sc, pert,
            r_ema, dt, fs, seed_id)
        elapsed = time.time() - t0
        if result is not None:
            geo_rows.append(result)
            if Q_slow is not None and Q_slow.shape[1] > 0:
                Q_list.append(Q_slow)
                seed_list.append(seed_id)
            print(f"  [{si+1:>2}/{len(seeds_727)}] {seed_id}: "
                  f"d={result.get('slow_dim','?')} "
                  f"mu={result.get('mu_phase',np.nan):.3f} "
                  f"frac_C={result.get('frac_C',0):.6f} "
                  f"cluster=[{result.get('rate_low',np.nan):.5f},"
                  f"{result.get('rate_high',np.nan):.5f}] "
                  f"({elapsed:.0f}s)")
        else:
            print(f"  [{si+1:>2}/{len(seeds_727)}] {seed_id}: FAILED")
    geo_df = pd.DataFrame(geo_rows)

    # ------ Cross-seed subspace comparison ------
    cross_angle_rows = []
    n_Q = len(Q_list)
    if n_Q >= 2:
        print(f"\n--- Cross-seed subspace comparison ({n_Q} bases) ---")
        for i in range(n_Q):
            for j in range(i+1, n_Q):
                # Principal angles between Q_list[i] and Q_list[j]
                # Pad to same dimension
                di, dj = Q_list[i].shape[1], Q_list[j].shape[1]
                M = Q_list[i].T @ Q_list[j]  # di × dj
                _, S, _ = np.linalg.svd(M, full_matrices=False)
                angles_ij = np.arccos(np.clip(S, 0.0, 1.0))
                proj_dist = float(np.linalg.norm(
                    Q_list[i] @ Q_list[i].T - Q_list[j] @ Q_list[j].T, 'fro'))
                cross_angle_rows.append({
                    "seed_i": seed_list[i], "seed_j": seed_list[j],
                    "dim_i": di, "dim_j": dj,
                    "max_angle_deg": float(np.max(angles_ij)) * 180.0 / np.pi,
                    "mean_angle_deg": float(np.mean(angles_ij)) * 180.0 / np.pi,
                    "proj_dist_fro": proj_dist,
                })
        cross_df = pd.DataFrame(cross_angle_rows)
        if len(cross_df) > 0:
            print(f"  Cross-seed max angle: {cross_df['max_angle_deg'].max():.4f}° "
                  f"(mean: {cross_df['max_angle_deg'].mean():.4f}°)")
        # Check for dimension mismatches
        dims_set = set(dims)
        if len(dims_set) > 1:
            print(f"  NOTE: Slow subspace dimensions vary across seeds: {sorted(dims_set)}")
            print(f"        Principal angles only measure overlap of the smaller subspace.")
    else:
        cross_df = pd.DataFrame()

    # ------ Average-projector representative (not Karcher mean) ------
    repr_dist_rows = []
    if n_Q >= 2:
        # Average-projector representative: dominant eigenspace of mean projector
        # Use the median dimension across seeds as the target dimension
        dims = [Q.shape[1] for Q in Q_list]
        d_median = int(np.median(dims))
        P_all = np.zeros((Q_list[0].shape[0], Q_list[0].shape[0]))
        for Q in Q_list:
            P_all += Q @ Q.T
        P_all /= n_Q
        ev_Pmean, eV_Pmean = np.linalg.eigh(P_all)
        Q_mean = eV_Pmean[:, -d_median:]  # top d_median eigenvectors
        P_mean = Q_mean @ Q_mean.T
        # Distance from each seed to the mean
        for i, Q in enumerate(Q_list):
            dist = float(np.linalg.norm(Q @ Q.T - P_mean, 'fro'))
            repr_dist_rows.append({
                "seed": seed_list[i],
                "dim": Q.shape[1],
                "dist_to_mean_fro": dist,
            })

    # ------ Average projector ------
    avg_proj_rows = []
    if n_Q >= 2:
        print(f"\n--- Average projector across {n_Q} seeds ---")
        # Build projectors, pad all to same ambient dimension
        n_ambient = Q_list[0].shape[0]
        P_avg = np.zeros((n_ambient, n_ambient))
        for Q in Q_list:
            P_avg += Q @ Q.T
        P_avg /= n_Q
        ev_P = np.linalg.eigvalsh(P_avg)
        ev_P_sorted = sorted(ev_P, reverse=True)
        for i, ev in enumerate(ev_P_sorted[:12]):
            avg_proj_rows.append({"index": i, "eigenvalue": float(ev)})
        print(f"  Top eigenvalues of average projector: "
              f"{[f'{x:.4f}' for x in ev_P_sorted[:8]]}")
    avg_proj_df = pd.DataFrame(avg_proj_rows)

    # ------ Sensitivity check ------
    sens_rows = []
    n_sens = min(args.sensitivity_seeds, n_Q)
    if n_sens >= 1:
        print(f"\n--- Sensitivity check on {n_sens} seed(s) ---")
        pert_levels = [pert * 0.5, pert, pert * 2.0]
        for si in range(n_sens):
            seed_id = seed_list[si]
            for pl in pert_levels:
                seed_file = run_dir / f"seed_{seed_id}.npz"
                with np.load(seed_file, allow_pickle=False) as data:
                    state = base.load_split_state(data, seed_id)
                for _ in range(fs):
                    inter = aug.base_intermediates(state, model, caps, A,
                                                    edges_mat, eps_sc)
                    aug.advance_base_state(state, inter)
                snap_fs = snapshot_state(state)
                inter_fs = aug.base_intermediates(state, model, caps, A,
                                                   edges_mat, eps_sc)
                aug.advance_base_state(state, inter_fs)
                v_after = extract_fundamental(state)
                restore_state(state, snap_fs)
                J = build_jacobian(state, snap_fs, aug, model, caps, A,
                                   edges_mat, eps_sc, pl, 18, v_after)
                evals = np.linalg.eigvals(J)
                abs_ev = np.abs(evals)
                rates = -np.log(np.maximum(abs_ev, 1e-300)) / dt
                sidx, rl, rh = identify_slow_cluster(rates, abs_ev, dt)
                n_sl = len(sidx) if sidx is not None else 0
                sens_rows.append({
                    "seed": seed_id,
                    "perturbation": pl,
                    "n_slow": n_sl,
                    "rate_low": rl,
                    "rate_high": rh,
                })
                print(f"  seed {seed_id} pert={pl:.0e}: n_slow={n_sl} "
                      f"cluster=[{rl:.5f},{rh:.5f}]" if sidx is not None
                      else f"  seed {seed_id} pert={pl:.0e}: no cluster")
    sens_df = pd.DataFrame(sens_rows)

    # ------ Output ------
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)
    safe_atomic_write_csv(od/"k3_structure_scan.csv", k3_df)
    if len(geo_df) > 0:
        safe_atomic_write_csv(od/"multiseed_geometry.csv", geo_df)
    if len(cross_df) > 0:
        safe_atomic_write_csv(od/"cross_seed_angles.csv", cross_df)
    if len(repr_dist_rows) > 0:
        pd.DataFrame(repr_dist_rows).to_csv(od/"representative_distances.csv", index=False)
    if len(avg_proj_df) > 0:
        safe_atomic_write_csv(od/"average_projector_eigenvalues.csv", avg_proj_df)
    if len(sens_df) > 0:
        safe_atomic_write_csv(od/"sensitivity_check.csv", sens_df)

    # ------ Report ------
    lines = [
        "="*70,
        "AIEF-1.4 Multi-Seed Slow Bundle Geometry (v2)",
        "="*70,
        f"Seeds scanned: {n_seeds}/{n_available}",
        f"Seeds with (7,2,7) winner map: {n_727} ({n_727/n_seeds*100:.1f}%)",
        f"Full geometry: {len(geo_df)} seeds",
        f"r_EMA: {r_ema:.6f}   alpha: {alpha:.12g}   dt: {dt}",
        "",
        "Survivorship note: results characterize the (7,2,7) attractor",
        f"family, not the entire model.  {n_727} of {n_seeds} seeds share",
        "this winner map.",
        "",
        "Spectral clustering: slow modes identified via largest gap in",
        "the rate spectrum, not a fixed ±1% band around r_EMA.",
        "",
        "─"*70,
        "K3 Winner Map Distribution:",
        "─"*70,
    ]
    if "winner_map" in k3_df.columns:
        for wm, count in k3_df["winner_map"].value_counts().items():
            lines.append(f"  {wm}: {count} seeds")
    lines.append("")

    if len(geo_df) > 0:
        lines.extend([
            "─"*70,
            "Geometry Diagnostics Across (7,2,7) Seeds:",
            "─"*70,
            f"  {'Metric':<32} {'min':>12} {'median':>12} {'max':>12}",
            f"  {'-'*32} {'-'*12} {'-'*12} {'-'*12}",
        ])
        lines.extend([
            f"  {'Metric':<32} {'min':>12} {'median':>12} {'max':>12} {'IQR':>12}",
            f"  {'-'*32} {'-'*12} {'-'*12} {'-'*12} {'-'*12}",
        ])
        for col, label in [
            ("mu_phase", "mu_phase"),
            ("max_angle_deg", "Max principal angle (°)"),
            ("frac_C", "C Frobenius fraction"),
            ("frac_scalar", "Scalar fraction"),
            ("lambda_variance", "Eigenvalue variance"),
            ("cond_num", "Eigenvector condition # (<100=well, >1000=unreliable)"),
            ("ratio_offdiag", "Off-diag / diag ratio"),
            ("nonnorm_ratio", "Non-normality ratio"),
            ("rate_low", "Cluster rate low"),
            ("rate_high", "Cluster rate high"),
        ]:
            if col in geo_df.columns:
                vals = geo_df[col].dropna()
                if len(vals) > 0:
                    q75, q25 = np.percentile(vals, [75, 25])
                    lines.append(
                        f"  {label:<32} {vals.min():>12.4e} "
                        f"{vals.median():>12.4e} {vals.max():>12.4e} "
                        f"{q75-q25:>12.4e}"
                    )

        # Per-seed detail
        lines.extend([
            "",
            "─"*70,
            "Per-Seed Detail:",
            "─"*70,
            f"  {'seed':<24} {'d':>3} {'mu':>7} {'ang':>7} "
            f"{'frac_C':>9} {'scalar':>7} {'cluster':>18}",
            f"  {'-'*24} {'-'*3} {'-'*7} {'-'*7} {'-'*9} {'-'*7} {'-'*18}",
        ])
        for _, r in geo_df.iterrows():
            cluster_str = f"[{r['rate_low']:.5f},{r['rate_high']:.5f}]"
            gap_str = f"gap={r.get('largest_gap',np.nan):.4f}" if 'largest_gap' in r else ""
            lines.append(
                f"  {str(r['seed']):<24} {int(r['slow_dim']):>3} "
                f"{r['mu_phase']:>7.4f} {r['max_angle_deg']:>7.4f} "
                f"{r['frac_C']:>9.6f} {r['frac_scalar']:>7.4f} "
                f"{cluster_str:>18}"
            )

        # Cross-seed subspace comparison
        if len(cross_df) > 0:
            mx = cross_df["max_angle_deg"].max()
            mn = cross_df["max_angle_deg"].min()
            avg = cross_df["max_angle_deg"].mean()
            pd_avg = cross_df["proj_dist_fro"].mean() if "proj_dist_fro" in cross_df.columns else np.nan
            lines.extend([
                "",
                "─"*70,
                "Cross-Seed Subspace Comparison:",
                "─"*70,
                f"  {len(cross_df)} pairwise comparisons among {n_Q} bases",
                f"  Max principal angle range: [{mn:.4f}°, {mx:.4f}°]",
                f"  Mean max angle: {avg:.4f}°",
                f"  Mean projector distance ‖P_i−P_j‖_F: {pd_avg:.4f}",
            ])
            if avg < 1.0:
                lines.append("  → Slow subspaces are tightly clustered (<1°).")
                lines.append("    Either outcome—universal or family—is structurally")
                lines.append("    informative.  See projector distances for symmetry.")
            elif avg < 5.0:
                lines.append("  → Slow subspaces show moderate variation (1-5°).")
                lines.append("    Consistent with a family of nearby invariant bundles.")
            else:
                lines.append("  → Substantial variation across seeds (>5°).")
                lines.append("    Each seed may have a distinct slow bundle orientation.")

        # Representative subspace distances
        if len(repr_dist_rows) > 0:
            gd = [r["dist_to_mean_fro"] for r in repr_dist_rows]
            radius = max(gd) if gd else 0.0
            lines.extend([
                "",
                "─"*70,
                "Distance to Representative Subspace (avg-projector):",
                "─"*70,
                f"  min={min(gd):.4f}  median={np.median(gd):.4f}  max={max(gd):.4f}",
                f"  Radius (max dist) = {radius:.4f}",
            ])

        # Average projector
        if len(avg_proj_df) > 0:
            ev_P = avg_proj_df["eigenvalue"].values
            n_near_one = int(np.sum(ev_P > 0.9))
            lines.extend([
                "",
                "─"*70,
                "Average Projector Eigenvalues:",
                "─"*70,
                f"  Top values: {[f'{x:.4f}' for x in ev_P[:8]]}",
                f"  Eigenvalues near 1 (>0.9): {n_near_one}",
            ])
            if n_near_one >= 7:
                lines.append("  → A 7-dimensional common slow subspace exists across seeds.")
            elif n_near_one >= 4:
                lines.append(f"  → A ~{n_near_one}-dimensional common subspace exists.")
            else:
                lines.append("  → No strongly common subspace across seeds.")

        # Sensitivity
        if len(sens_df) > 0:
            lines.extend([
                "",
                "─"*70,
                "Finite-Difference Sensitivity (perturbation level only):",
                "─"*70,
            ])
            for seed_id in sens_df["seed"].unique():
                sub = sens_df[sens_df["seed"] == seed_id]
                lines.append(f"  seed {seed_id}:")
                for _, r in sub.iterrows():
                    lines.append(
                        f"    pert={r['perturbation']:.0e}  n_slow={int(r['n_slow'])}  "
                        f"cluster=[{r['rate_low']:.5f},{r['rate_high']:.5f}]"
                    )

        # Variability summary
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
            ])
            if c_std < 1e-4 and mu_std < 0.01 and scalar_std < 1e-4:
                lines.append("  → All metrics are tightly clustered.")
            elif c_std < 1e-2:
                lines.append("  → Moderate variation.  Qualitative structure persists.")
            else:
                lines.append("  → Substantial variation detected.")
    else:
        lines.append("  No (7,2,7) seeds for geometry analysis.")

    lines.extend([
        "",
        "Evidence class: robustness analysis across seeds.",
        "Characterizes the (7,2,7) winner-map attractor family.",
        "Limited to one linearization point per seed (final step).",
        "Does not establish robustness along trajectories or across",
        "different operating points on the attractor.",
        "Does not establish generality across all AIEF trajectories.",
    ])

    report = "\n".join(lines)
    safe_atomic_write_text(od/"multiseed_geometry_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 multi-seed slow bundle geometry v2",
        "n_seeds_scanned": n_seeds,
        "n_727_seeds": n_727,
        "n_geometry_computed": len(geo_df),
        "n_cross_comparisons": len(cross_df),
        "survivorship_note": "characterizes (7,2,7) attractor family only",
        "parameters": {"dt":dt, "r_EMA":r_ema, "alpha":alpha,
                        "perturbation":pert},
        "outputs": ["k3_structure_scan.csv", "multiseed_geometry.csv",
                     "cross_seed_angles.csv", "average_projector_eigenvalues.csv",
                     "sensitivity_check.csv", "multiseed_geometry_report.txt",
                     "analysis_manifest.json"],
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")
    print(report)
    print(f"\nDone. → {od.resolve()}")

if __name__ == "__main__":
    main()
