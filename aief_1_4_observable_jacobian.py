#!/usr/bin/env python3

"""
AIEF-1.4 Observable Jacobian Projection

Computes the linearized sensitivity of each measured observable to the
18 fundamental K3 state variables at the final replay step, then
projects that sensitivity onto the slow invariant subspace.

For each observable O:
  D_O[j] = ∂O/∂(state_j)            (1×18 gradient via finite differences)
  frac_slow = ‖D_O · Q_slow‖² / ‖D_O‖²
  frac_h, frac_B, frac_C = variable-group decomposition of D_O

This answers: "How much of each observable's local sensitivity comes
from the slow coherence subspace vs. the fast B/history directions?"

No nonlinear reconstruction.  No trajectory replay.  No ill-conditioned
variance ratios.  Just the geometry of the observable function at the
fixed point.

Runs the full Jacobian (18 columns) + observable gradients (6 × 18 columns).
Expect 2-4 minutes.

Outputs:
  observable_jacobian.csv
  observable_jacobian_report.txt
  analysis_manifest.json
"""

from __future__ import annotations

import argparse, copy, hashlib, json, math, os, sys, tempfile
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_observable_jacobian"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_PERTURBATION = 1e-8

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

def finite_diff_response(col, state, snap_fs, caps, model, A, edges_mat, eps_sc,
                         aug, v_before, pert, n_vars):
    """Advance one step with perturbation in variable `col`, return perturbed state vector."""
    restore_state(state, snap_fs)
    vc = extract_fundamental(state)
    delta = pert * max(1.0, abs(vc[col]))
    vc[col] += delta
    inject_fundamental(state, vc)
    inter_p = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    aug.advance_base_state(state, inter_p)
    return extract_fundamental(state)

# ── CLI ─────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--npz", default=DEFAULT_NPZ)
    p.add_argument("--manifest", default=DEFAULT_MANIFEST)
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--seed", default=DEFAULT_SEED)
    p.add_argument("--dt", type=float, default=DEFAULT_DT)
    p.add_argument("--scale-epsilon", type=float, default=DEFAULT_SCALE_EPSILON)
    p.add_argument("--perturbation", type=float, default=DEFAULT_PERTURBATION)
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

    # ── Replay to final step ──
    print("Replaying to final step …")
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)
    for step in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter)

    snap_fs = snapshot_state(state)
    inter_fs = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    v_baseline = extract_fundamental(state)
    n_vars = len(v_baseline)
    print(f"  State dimension: {n_vars}")

    # ── Full 18×18 Jacobian (needed for slow subspace) ──
    print("Building 18×18 augmented Jacobian …")
    aug.advance_base_state(state, inter_fs)
    v_after = extract_fundamental(state)
    J_full = np.zeros((n_vars, n_vars))
    for col in range(n_vars):
        vp = finite_diff_response(col, state, snap_fs, caps, model, A, edges_mat,
                                   eps_sc, aug, v_baseline, pert, n_vars)
        J_full[:, col] = (vp - v_after) / pert
        if (col+1) % 6 == 0: print(f"  J_full column {col+1}/{n_vars}")
    print("  done.")

    # ── Slow subspace ──
    evals, evecs_r = np.linalg.eig(J_full)
    abs_evals = np.abs(evals)
    rates = -np.log(np.maximum(abs_evals, 1e-300))/dt
    slow_mask = (rates > r_ema*0.99) & (rates < r_ema*1.01) & (abs_evals < 1.0)
    slow_idx = np.where(slow_mask)[0]
    Q_slow = build_real_slow_basis(evecs_r, slow_idx)
    slow_dim = Q_slow.shape[1]
    Pi_slow = Q_slow @ Q_slow.T
    Pi_fast = np.eye(n_vars) - Pi_slow

    # Now compute SVD of normalized complex slow eigenvectors
    V_slow_c = evecs_r[:, slow_idx]
    V_slow_c = V_slow_c / (np.linalg.norm(V_slow_c, axis=0) + 1e-300)
    Uc, Sc, Vhc = np.linalg.svd(V_slow_c, full_matrices=False)
    cumvar = np.cumsum(Sc**2)/np.sum(Sc**2)
    eff_dim = int(np.sum(cumvar < 0.95)) + 1

    # ── Eigenvector composition (full precision) ──
    decomp_rows = []
    for k in range(len(slow_idx)):
        v = V_slow_c[:, k]
        h_p = float(np.sum(np.abs(v[0:3])**2))
        B_p = float(np.sum(np.abs(v[3:6])**2))
        C_p = float(np.sum(np.abs(v[6:18])**2))
        tot = h_p + B_p + C_p + 1e-300
        decomp_rows.append({
            "mode": k, "rate": float(rates[slow_idx[k]]),
            "frac_h": h_p/tot, "frac_B": B_p/tot, "frac_C": C_p/tot,
            "|h|_max": float(np.max(np.abs(v[0:3]))),
            "|B|_max": float(np.max(np.abs(v[3:6]))),
        })
    decomp_df = pd.DataFrame(decomp_rows)

    # Pairwise overlaps
    omat = np.abs(V_slow_c.T.conj() @ V_slow_c)
    offdiag = [float(omat[i,j]) for i in range(len(slow_idx))
               for j in range(len(slow_idx)) if i!=j]
    mean_overlap = float(np.mean(offdiag)) if offdiag else 0.0

    # ── Maintain state at pre-advance (before step) for observable gradient ──
    restore_state(state, snap_fs)
    inter_fs2 = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)

    # ── Baseline observables ──
    def compute_observables(intermediate):
        Rmat = intermediate["R"]
        xp = intermediate["x"]; qs = intermediate["q_scale"]
        s7 = caps[7]/(float(qs[7])+eps_sc); s2 = caps[2]/(float(qs[2])+eps_sc)
        return np.array([
            float(xp[25] - xp[59]),                         # d_L
            float(xp[59] - xp[29]),                         # d_R
            float(s2 - s7),                                  # s2 - s7
            float(xp[25]*s7/(float(qs[7])+eps_sc)
                  - xp[59]*s7/(float(qs[7])+eps_sc)),       # beta25 - beta59
            float(Rmat[2,7] - Rmat[7,11]),                   # resonance_gap_L
            float(Rmat[7,11] - Rmat[2,11]),                  # resonance_gap_R
        ])

    obs_names = ["d_L", "d_R", "s2_minus_s7", "beta25_minus_beta59",
                 "resonance_gap_L", "resonance_gap_R"]
    obs_base = compute_observables(inter_fs2)

    # ── Observable Jacobians ──
    print("Computing observable gradients (D_O for each observable) …")
    D_obs = np.zeros((len(obs_names), n_vars))  # 6 × 18

    for col in range(n_vars):
        # Perturb state, compute intermediate, measure observable change
        restore_state(state, snap_fs)
        vc = extract_fundamental(state)
        delta = pert * max(1.0, abs(vc[col]))
        vc[col] += delta
        inject_fundamental(state, vc)
        inter_pert = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        obs_pert = compute_observables(inter_pert)
        D_obs[:, col] = (obs_pert - obs_base) / delta
        if (col+1) % 6 == 0:
            print(f"  D_O column {col+1}/{n_vars}")

    print("  done.")

    # ── Project each D_O onto slow/fast subspaces ──
    var_labels = (
        [f"h_old_{i}" for i in K3_NODES]
        + [f"B_{e}" for _,_,e in K3_EDGE_LIST]
        + [f"C_{ia}{ib}_re" for ia,ib in DIRECTED_PAIRS]
        + [f"C_{ia}{ib}_im" for ia,ib in DIRECTED_PAIRS]
    )

    obs_rows = []
    for k, name in enumerate(obs_names):
        d = D_obs[k, :]   # 1×18 gradient
        norm_sq = float(d @ d)
        norm = math.sqrt(max(norm_sq, 1e-300))

        # Projections
        d_slow = d @ Pi_slow     # projection onto slow subspace
        d_fast = d @ Pi_fast     # projection onto fast complement
        slow_norm_sq = float(d_slow @ d_slow)
        fast_norm_sq = float(d_fast @ d_fast)

        frac_slow = slow_norm_sq / (norm_sq + 1e-300)
        frac_fast = fast_norm_sq / (norm_sq + 1e-300)

        # Variable-group decomposition of the full gradient
        h_p = float(np.sum(d[0:3]**2))
        B_p = float(np.sum(d[3:6]**2))
        C_p = float(np.sum(d[6:18]**2))
        tot_p = h_p + B_p + C_p + 1e-300

        # Variable-group decomposition of the slow-projected gradient
        d_slow_arr = np.asarray(d_slow, dtype=float)
        h_ps = float(np.sum(d_slow_arr[0:3]**2))
        B_ps = float(np.sum(d_slow_arr[3:6]**2))
        C_ps = float(np.sum(d_slow_arr[6:18]**2))
        tot_ps = h_ps + B_ps + C_ps + 1e-300

        # Top 5 state variables by absolute sensitivity
        abs_d = np.abs(d)
        top_idx = np.argsort(-abs_d)[:5]

        obs_rows.append({
            "observable": name,
            "gradient_norm": float(norm),
            "frac_slow": float(frac_slow),
            "frac_fast": float(frac_fast),
            # Full gradient decomposition
            "frac_h_full": float(h_p/tot_p),
            "frac_B_full": float(B_p/tot_p),
            "frac_C_full": float(C_p/tot_p),
            # Slow-projected gradient decomposition
            "frac_h_slow": float(h_ps/tot_ps),
            "frac_B_slow": float(B_ps/tot_ps),
            "frac_C_slow": float(C_ps/tot_ps),
            # Top contributors
            "top1_var": var_labels[top_idx[0]],
            "top1_val": float(abs_d[top_idx[0]]),
            "top2_var": var_labels[top_idx[1]],
            "top2_val": float(abs_d[top_idx[1]]),
            "top3_var": var_labels[top_idx[2]],
            "top3_val": float(abs_d[top_idx[2]]),
            "top4_var": var_labels[top_idx[3]],
            "top4_val": float(abs_d[top_idx[3]]),
            "top5_var": var_labels[top_idx[4]],
            "top5_val": float(abs_d[top_idx[4]]),
        })

    obs_df = pd.DataFrame(obs_rows)

    # ── Output ──
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)
    safe_atomic_write_csv(od/"observable_jacobian.csv", obs_df)
    safe_atomic_write_csv(od/"eigenvector_decomposition.csv", decomp_df)

    # ── Report ──
    mean_frac_slow = float(np.mean(obs_df["frac_slow"]))

    lines = [
        "="*70,
        "AIEF-1.4 Observable Jacobian Projection",
        "="*70,
        f"r_EMA: {r_ema:.6f}   alpha: {alpha:.12g}   dt: {dt}",
        f"Slow EMA-cluster modes: {len(slow_idx)}",
        f"Real slow subspace dimension: {slow_dim}",
        f"Effective dimension (95% SVD): {eff_dim}",
        f"Mean pairwise eigenvector overlap: {mean_overlap:.4f}",
        "",
        "Method: D_O = gradient of each observable w.r.t. the 18 fundamental",
        "K3 state variables, computed via finite differences at the final step.",
        "Each D_O is projected onto the slow subspace Q_slow.",
        "frac_slow = ||D_O · Π_slow||² / ||D_O||².",
        "",
        "─"*70,
        "Observable Sensitivity Decomposition:",
        "─"*70,
        f"  {'Observable':<24} {'‖D_O‖':>10} {'%slow':>8} {'%fast':>8} "
        f"{'%h':>6} {'%B':>6} {'%C':>6}",
        f"  {'-'*24} {'-'*10} {'-'*8} {'-'*8} {'-'*6} {'-'*6} {'-'*6}",
    ]
    for _, r in obs_df.iterrows():
        lines.append(
            f"  {r['observable']:<24} {r['gradient_norm']:>10.4e} "
            f"{r['frac_slow']*100:>8.1f} {r['frac_fast']*100:>8.1f} "
            f"{r['frac_h_full']*100:>6.1f} {r['frac_B_full']*100:>6.1f} "
            f"{r['frac_C_full']*100:>6.1f}"
        )
    lines.extend([
        "",
        f"  Mean slow-subspace fraction: {mean_frac_slow*100:.1f}%",
        "",
    ])

    if mean_frac_slow > 0.95:
        lines.append("  The slow subspace dominates the local sensitivity of every")
        lines.append("  measured observable.  At the linearized level, the observables")
        lines.append("  are almost entirely functions of the slow coherence dynamics.")
        lines.append("  The single-rate inheritance is explained by the geometry of")
        lines.append("  the observable map itself, not just by trajectory alignment.")
    elif mean_frac_slow > 0.70:
        lines.append("  The slow subspace accounts for a majority of observable")
        lines.append("  sensitivity, but fast directions contribute measurably.")
    else:
        lines.append("  Fast directions contribute substantially to observable")
        lines.append("  sensitivity at the linearized level.")

    # Top contributors per observable
    lines.extend([
        "",
        "─"*70,
        "Top State-Variable Contributors to Each Observable:",
        "─"*70,
    ])
    for _, r in obs_df.iterrows():
        lines.append(f"  {r['observable']}:")
        for i in range(1, 6):
            lines.append(
                f"    {r[f'top{i}_var']:<14} {r[f'top{i}_val']:.4e}"
            )

    # Slow-projected gradient decomposition
    lines.extend([
        "",
        "─"*70,
        "Slow-Projected Gradient Decomposition:",
        "─"*70,
        f"  {'Observable':<24} {'%h_slow':>8} {'%B_slow':>8} {'%C_slow':>8}",
        f"  {'-'*24} {'-'*8} {'-'*8} {'-'*8}",
    ])
    for _, r in obs_df.iterrows():
        lines.append(
            f"  {r['observable']:<24} "
            f"{r['frac_h_slow']*100:>8.1f} {r['frac_B_slow']*100:>8.1f} "
            f"{r['frac_C_slow']*100:>8.1f}"
        )

    # Eigenvector composition summary
    lines.extend([
        "",
        "─"*70,
        "Slow Eigenvector Composition (full precision):",
        "─"*70,
        f"  {'Mode':>5} {'rate':>10} {'frac_h':>14} {'frac_B':>14} {'frac_C':>14}"
        f"  {'|h|_max':>12} {'|B|_max':>12}",
        f"  {'-'*5} {'-'*10} {'-'*14} {'-'*14} {'-'*14} {'-'*12} {'-'*12}",
    ])
    for _, r in decomp_df.iterrows():
        lines.append(
            f"  {r['mode']:>5} {r['rate']:>10.6f} "
            f"{r['frac_h']:>14.4e} {r['frac_B']:>14.4e} {r['frac_C']:>14.4e}"
            f"  {r['|h|_max']:>12.4e} {r['|B|_max']:>12.4e}"
        )
    mh = float(np.mean(decomp_df["frac_h"]))
    mB = float(np.mean(decomp_df["frac_B"]))
    mC = float(np.mean(decomp_df["frac_C"]))
    lines.append(
        f"  {'mean':>5} {'':>10} {mh:>14.4e} {mB:>14.4e} {mC:>14.4e}"
    )

    # SVD
    lines.extend([
        "",
        "─"*70,
        "SVD of slow eigenvector stack:",
        "─"*70,
        f"  {'Index':>6} {'Singular value':>16} {'Cumulative %':>14}",
        f"  {'-'*6} {'-'*16} {'-'*14}",
    ])
    for i in range(len(Sc)):
        lines.append(f"  {i:>6} {Sc[i]:>16.6e} {cumvar[i]*100:>14.1f}")
    lines.extend([
        "",
        f"  Effective rank (95%): {eff_dim}/{len(slow_idx)}",
    ])

    report = "\n".join(lines)
    safe_atomic_write_text(od/"observable_jacobian_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 observable Jacobian projection",
        "seed": args.seed,
        "parameters": {"dt":dt, "r_EMA":r_ema, "alpha":alpha, "perturbation":pert},
        "slow_dim": slow_dim, "effective_slow_dim": eff_dim,
        "mean_pairwise_overlap": mean_overlap,
        "mean_observable_slow_fraction": mean_frac_slow,
        "h_machine_zero": bool(mh < 1e-12),
        "B_suppression_factor": 1.0/(mB + 1e-300) if mB > 1e-30 else float('inf'),
        "outputs": ["observable_jacobian.csv",
                     "eigenvector_decomposition.csv",
                     "observable_jacobian_report.txt",
                     "analysis_manifest.json"],
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")
    print(report)
    print(f"\nDone. → {od.resolve()}")

if __name__ == "__main__":
    main()
