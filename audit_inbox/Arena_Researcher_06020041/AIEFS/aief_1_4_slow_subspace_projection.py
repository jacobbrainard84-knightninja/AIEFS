#!/usr/bin/env python3

"""
AIEF-1.4 Slow Subspace Projection (v2 — complex-aware)

Builds the 18x18 augmented Jacobian, extracts the EMA-cluster
eigenvectors, constructs a REAL orthonormal basis for the slow
invariant subspace (handling complex-conjugate pairs correctly),
and projects the measured replay observables onto that subspace.

Fixes from v1:
  - Real projection basis built from Re/Im of complex eigenvector pairs
  - No ComplexWarning: projection always yields real state vectors
  - Variance fraction = var(obs_slow) / var(obs_full)  (standard R²-like)
  - Full-precision reporting of variable-group fractions

Key question: do the observables follow the temporal pattern of the
slow coherence subspace?
"""

from __future__ import annotations

import argparse, copy, hashlib, json, math, os, sys, tempfile
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_slow_subspace_projection"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_PERTURBATION = 1e-8

K3_NODES = [2, 7, 11]
K3_EDGE_LIST = [(2,7,25), (2,11,29), (7,11,59)]
DIRECTED_PAIRS = [(2,7),(7,2),(2,11),(11,2),(7,11),(11,7)]

# ── utilities ──
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
    """Inject a real 18-vector into the state.  All entries must be real."""
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
    """
    Given complex eigenvectors (columns of evecs_complex) and indices of slow
    modes, build a REAL orthonormal basis for the slow invariant subspace.

    Complex eigenvectors come in conjugate pairs for a real matrix.
    For each pair (v, v̄), the real basis vectors are Re(v) and Im(v).
    For a purely real eigenvector, just use the vector itself.
    """
    real_basis = []
    used = set()
    for i in slow_idx:
        if i in used:
            continue
        v = evecs_complex[:, i]
        if abs(v.imag).max() < tol:
            # Purely real eigenvector
            real_basis.append(np.asarray(v.real, dtype=float).copy())
            used.add(i)
        else:
            # Complex eigenvector — find its conjugate partner
            partner = None
            for j in slow_idx:
                if j == i or j in used:
                    continue
                w = evecs_complex[:, j]
                if np.allclose(v.real, w.real, atol=tol) and \
                   np.allclose(v.imag, -w.imag, atol=tol):
                    partner = j
                    break
            real_basis.append(np.asarray(v.real, dtype=float).copy())
            real_basis.append(np.asarray(v.imag, dtype=float).copy())
            used.add(i)
            if partner is not None:
                used.add(partner)
    if not real_basis:
        return np.zeros((evecs_complex.shape[0], 0), dtype=float)
    basis_mat = np.column_stack(real_basis)
    # QR to orthonormalize
    Q, _ = np.linalg.qr(basis_mat)
    return Q

# ── CLI ──
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

# ── main ──
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

    # ── Replay to final step, build Jacobian ──
    print("Replaying to final step …")
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)
    for step in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter)

    print("Building 18×18 augmented Jacobian …")
    snap_fs = snapshot_state(state)
    inter_base = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    aug.advance_base_state(state, inter_base)
    v_after = extract_fundamental(state)
    n_vars = len(v_after)
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
        J[:, col] = (vp - v_after)/delta
    print("  done.")

    # ── Eigendecomposition ──
    evals, evecs_r = np.linalg.eig(J)
    abs_evals = np.abs(evals)
    rates = -np.log(np.maximum(abs_evals, 1e-300))/dt
    slow_mask = (rates > r_ema*0.99) & (rates < r_ema*1.01) & (abs_evals < 1.0)
    slow_idx = np.where(slow_mask)[0]
    slow_idx = slow_idx[np.argsort(rates[slow_idx])]
    n_slow = len(slow_idx)
    print(f"  Slow EMA-cluster modes: {n_slow}")

    # ── Build REAL orthonormal basis for slow subspace ──
    Q_slow = build_real_slow_basis(evecs_r, slow_idx)
    slow_dim = Q_slow.shape[1]
    print(f"  Real slow subspace dimension: {slow_dim}")

    # Normalize complex eigenvectors for decomposition/overlap analysis
    V_slow_c = evecs_r[:, slow_idx]
    V_slow_c = V_slow_c / (np.linalg.norm(V_slow_c, axis=0) + 1e-300)

    # SVD of complex slow eigenvector stack
    Uc, Sc, Vhc = np.linalg.svd(V_slow_c, full_matrices=False)
    cumvar = np.cumsum(Sc**2)/np.sum(Sc**2)
    eff_dim = int(np.sum(cumvar < 0.95)) + 1

    # ── Replay to collect observables AND project onto slow subspace ──
    # Both done in a single pass: snapshot/restore at each step so that
    # the slow-projected observable is computed from the same trajectory
    # state as the full observable.
    print("Replaying, collecting + projecting observables …")
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)

    time_vec = np.arange(fs) * dt
    obs_full = {
        "d_L": np.zeros(fs), "d_R": np.zeros(fs),
        "s2_minus_s7": np.zeros(fs), "beta25_minus_beta59": np.zeros(fs),
        "resonance_gap_L": np.zeros(fs), "resonance_gap_R": np.zeros(fs),
    }
    obs_slow_arr = {k: np.zeros(fs) for k in obs_full}

    for step in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)

        # ── Full observable ──
        Rmat = inter["R"]
        xp = inter["x"]; qs = inter["q_scale"]
        s7 = caps[7]/(float(qs[7])+eps_sc); s2 = caps[2]/(float(qs[2])+eps_sc)
        obs_full["d_L"][step] = float(xp[25]-xp[59])
        obs_full["d_R"][step] = float(xp[59]-xp[29])
        obs_full["s2_minus_s7"][step] = float(s2-s7)
        obs_full["beta25_minus_beta59"][step] = float(
            xp[25]*s7/(float(qs[7])+eps_sc) - xp[59]*s7/(float(qs[7])+eps_sc))
        obs_full["resonance_gap_L"][step] = float(Rmat[2,7]-Rmat[7,11])
        obs_full["resonance_gap_R"][step] = float(Rmat[7,11]-Rmat[2,11])

        # ── Slow-projected observable ──
        sv = extract_fundamental(state)
        sv_slow = Q_slow @ (Q_slow.T @ sv)   # real projection, no ComplexWarning

        snap_step = snapshot_state(state)     # save current step
        inject_fundamental(state, sv_slow)
        inter_slow = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        Rmat_s = inter_slow["R"]
        xp_s = inter_slow["x"]; qs_s = inter_slow["q_scale"]
        s7s = caps[7]/(float(qs_s[7])+eps_sc); s2s = caps[2]/(float(qs_s[2])+eps_sc)

        obs_slow_arr["d_L"][step] = float(xp_s[25]-xp_s[59])
        obs_slow_arr["d_R"][step] = float(xp_s[59]-xp_s[29])
        obs_slow_arr["s2_minus_s7"][step] = float(s2s-s7s)
        obs_slow_arr["beta25_minus_beta59"][step] = float(
            xp_s[25]*s7s/(float(qs_s[7])+eps_sc) - xp_s[59]*s7s/(float(qs_s[7])+eps_sc))
        obs_slow_arr["resonance_gap_L"][step] = float(Rmat_s[2,7]-Rmat_s[7,11])
        obs_slow_arr["resonance_gap_R"][step] = float(Rmat_s[7,11]-Rmat_s[2,11])

        restore_state(state, snap_step)       # restore to current step
        aug.advance_base_state(state, inter)  # advance normally

    # Build projection DataFrame
    proj_rows = []
    for step in range(fs):
        row = {"step": step, "time": time_vec[step]}
        for k in obs_full:
            row[f"full_{k}"] = float(obs_full[k][step])
            row[f"slow_{k}"] = float(obs_slow_arr[k][step])
        proj_rows.append(row)
    proj_df = pd.DataFrame(proj_rows)

    # ── Variance fractions (simple, standard) ──
    variance_rows = []
    for k in ["d_L","d_R","s2_minus_s7","beta25_minus_beta59",
              "resonance_gap_L","resonance_gap_R"]:
        full = proj_df[f"full_{k}"].values
        slow = proj_df[f"slow_{k}"].values
        var_full = np.var(full)
        var_slow = np.var(slow)
        corr = np.corrcoef(slow, full)[0,1] if var_full > 1e-30 and var_slow > 1e-30 else 0.0
        variance_rows.append({
            "observable": k,
            "var_full": float(var_full),
            "var_slow": float(var_slow),
            "frac_var": float(var_slow/(var_full+1e-30)),
            "correlation": float(corr),
        })
    var_df = pd.DataFrame(variance_rows)

    # ── Eigenvector decomposition (full precision) ──
    decomp_rows = []
    for k in range(n_slow):
        v = V_slow_c[:, k]
        h_p = float(np.sum(np.abs(v[0:3])**2))
        B_p = float(np.sum(np.abs(v[3:6])**2))
        C_p = float(np.sum(np.abs(v[6:18])**2))
        tot = h_p + B_p + C_p + 1e-300
        decomp_rows.append({
            "mode": k, "rate": float(rates[slow_idx[k]]),
            "frac_h": h_p/tot, "frac_B": B_p/tot, "frac_C": C_p/tot,
            "h_min": float(np.min(np.abs(v[0:3]))),
            "h_max": float(np.max(np.abs(v[0:3]))),
            "B_min": float(np.min(np.abs(v[3:6]))),
            "B_max": float(np.max(np.abs(v[3:6]))),
        })
    decomp_df = pd.DataFrame(decomp_rows)

    # ── Pairwise overlaps (complex inner products) ──
    omat = np.abs(V_slow_c.T.conj() @ V_slow_c)
    offdiag = [float(omat[i,j]) for i in range(n_slow) for j in range(n_slow) if i!=j]
    mean_overlap = float(np.mean(offdiag)) if offdiag else 0.0

    # ── Output ──
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)
    safe_atomic_write_csv(od/"observable_projections.csv", proj_df)
    safe_atomic_write_csv(od/"variance_fractions.csv", var_df)
    safe_atomic_write_csv(od/"eigenvector_decomposition.csv", decomp_df)

    # ── Report ──
    lines = [
        "="*70,
        "AIEF-1.4 Slow Subspace Projection (v2 — complex-aware)",
        "="*70,
        f"r_EMA: {r_ema:.6f}   alpha: {alpha:.12g}   dt: {dt}",
        f"Slow EMA-cluster eigenvalues: {n_slow}",
        f"Real slow subspace dimension: {slow_dim}",
        f"Effective dimension (95% SVD): {eff_dim}",
        f"Mean pairwise overlap: {mean_overlap:.4f}",
        "",
        "─"*70,
        "Observable alignment with slow subspace:",
        "─"*70,
        f"  {'Observable':<24} {'var(slow)/var(full)':>20} {'correlation':>14}",
        f"  {'-'*24} {'-'*20} {'-'*14}",
    ]
    for _, r in var_df.iterrows():
        lines.append(
            f"  {r['observable']:<24} {r['frac_var']:>20.4f} {r['correlation']:>14.6f}"
        )
    lines.append("")

    mean_frac = float(np.mean(var_df["frac_var"]))
    mean_corr = float(np.mean(np.abs(var_df["correlation"])))
    if mean_corr > 0.95:
        lines.append(f"  Mean |correlation| = {mean_corr:.4f}.")
        lines.append("  The slow subspace captures the temporal pattern")
        lines.append("  of every observable.  The low variance fractions")
        lines.append("  indicate that amplitude is generated outside the")
        lines.append("  slow subspace — consistent with fast B/history")
        lines.append("  variables contributing amplitude but not rhythm.")
    elif mean_corr > 0.80:
        lines.append(f"  Mean |correlation| = {mean_corr:.4f}.")
        lines.append("  Moderate temporal alignment.")
    else:
        lines.append(f"  Mean |correlation| = {mean_corr:.4f}.")
        lines.append("  Weak temporal alignment.")

    # ── Eigenvector composition ──
    lines.extend([
        "",
        "─"*70,
        "Variable-group composition (full precision):",
        "─"*70,
        f"  {'Mode':>5} {'rate':>10} {'frac_h':>14} {'frac_B':>14} {'frac_C':>14}"
        f"  {'|h|_max':>12} {'|B|_max':>12}",
        f"  {'-'*5} {'-'*10} {'-'*14} {'-'*14} {'-'*14} {'-'*12} {'-'*12}",
    ])
    for _, r in decomp_df.iterrows():
        lines.append(
            f"  {r['mode']:>5} {r['rate']:>10.6f} "
            f"{r['frac_h']:>14.4e} {r['frac_B']:>14.4e} {r['frac_C']:>14.4e}"
            f"  {r['h_max']:>12.4e} {r['B_max']:>12.4e}"
        )
    mh, mB, mC = [float(np.mean(decomp_df[c])) for c in ["frac_h","frac_B","frac_C"]]
    lines.append(
        f"  {'mean':>5} {'':>10} {mh:>14.4e} {mB:>14.4e} {mC:>14.4e}"
    )
    lines.append("")

    if mh < 1e-12 and mB < 1e-12:
        lines.append("  h_old and B components are at machine-zero levels.")
        lines.append("  The slow subspace is structurally confined to C.")
    elif mh < 1e-6 and mB < 1e-6:
        lines.append("  h_old and B components are suppressed by >6 orders")
        lines.append("  of magnitude relative to C.  Effectively C-dominated.")
    else:
        lines.append("  h_old and/or B have non-negligible slow components.")

    # ── SVD ──
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
        f"  Effective rank (95%): {eff_dim}/{n_slow}",
    ])

    if eff_dim == 1:
        lines.append("  Effectively rank-1.  One slow mechanism.")
    elif eff_dim <= 2:
        lines.append(f"  Low effective dimension ({eff_dim}).")
    else:
        lines.append(f"  Genuinely {eff_dim}-dimensional slow subspace.")

    report = "\n".join(lines)
    safe_atomic_write_text(od/"slow_subspace_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 slow subspace projection v2",
        "seed": args.seed,
        "parameters": {"dt":dt, "r_EMA":r_ema, "alpha":alpha, "perturbation":pert},
        "n_slow_modes": n_slow, "real_slow_dim": slow_dim,
        "effective_slow_dim": eff_dim,
        "mean_pairwise_overlap": mean_overlap,
        "mean_observable_correlation": mean_corr,
        "mean_variance_fraction": mean_frac,
        "h_B_machine_zero": bool(mh < 1e-12 and mB < 1e-12),
        "outputs": ["observable_projections.csv", "variance_fractions.csv",
                     "eigenvector_decomposition.csv", "slow_subspace_report.txt",
                     "analysis_manifest.json"],
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")
    print(report)
    print(f"\nDone. → {od.resolve()}")

if __name__ == "__main__":
    main()
