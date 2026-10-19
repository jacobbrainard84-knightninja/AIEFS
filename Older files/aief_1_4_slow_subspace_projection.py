#!/usr/bin/env python3

"""
AIEF-1.4 Slow Subspace Projection

Builds the 18x18 augmented Jacobian, extracts the EMA-cluster
eigenvectors, and projects the measured replay observables onto
the slow invariant subspace.

Questions answered:
  - Effective dimension of the slow subspace (SVD)
  - Variable-group composition of slow eigenvectors
  - Pairwise overlaps
  - Participation factors
  - Fraction of each observable's variance captured by span(V_slow)

If all observables have >95% variance in the slow subspace,
they share a single invariant mechanism — not just coincident rates.
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

# ── utilities ────────────────────────────────────────────────────────
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

# ── state I/O ─────────────────────────────────────────────────────────
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
    return np.array(v)

def inject_fundamental(state, vec):
    Bm, Cm = state.B, state.coherence_acc
    idx = 0
    ho = {i:vec[idx+i2] for i2,i in enumerate(K3_NODES)}; idx += 3
    hl = list(state.history)
    if hl:
        oldest = hl[0].copy()
        for i in K3_NODES: oldest[i] = ho[i]
        hl[0] = oldest; state.history.clear()
        for e in hl: state.history.append(e)
    for _,_,e in K3_EDGE_LIST:
        ia,ib = (2,7) if e==25 else ((2,11) if e==29 else (7,11))
        v = vec[idx]; idx += 1; Bm[ia,ib] = Bm[ib,ia] = v
    for ia,ib in DIRECTED_PAIRS:
        re,im = vec[idx], vec[idx+1]; idx += 2
        Cm[ia,ib] = complex(re,im)

# ── CLI ────────────────────────────────────────────────────────────────
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

# ── main ───────────────────────────────────────────────────────────────
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

    # ── Jacobian ──
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
    V_slow = evecs_r[:, slow_idx]                      # 18 × n_slow
    V_slow = V_slow / (np.linalg.norm(V_slow, axis=0) + 1e-300)
    n_slow = len(slow_idx)

    # SVD of V_slow stack
    U, S, Vh = np.linalg.svd(V_slow, full_matrices=False)
    cumvar = np.cumsum(S**2)/np.sum(S**2)
    eff_dim = int(np.sum(cumvar < 0.95)) + 1

    # ── Replay to collect observables ──
    print("Replaying to collect observable timeseries …")
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)

    time_vec = np.arange(fs) * dt
    obs = {
        "alignment_residual": np.zeros(fs),
        "d_L": np.zeros(fs),
        "d_R": np.zeros(fs),
        "s2_minus_s7": np.zeros(fs),
        "beta25_minus_beta59": np.zeros(fs),
        "resonance_gap_L": np.zeros(fs),
        "resonance_gap_R": np.zeros(fs),
    }

    for step in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        Rmat = inter["R"]
        xp = inter["x"]
        qs = inter["q_scale"]
        s7 = caps[7]/(float(qs[7])+eps_sc)
        s2 = caps[2]/(float(qs[2])+eps_sc)
        beta25 = float(xp[25])*s7/(float(qs[7])+eps_sc)
        beta59 = float(xp[59])*s7/(float(qs[7])+eps_sc)

        obs["alignment_residual"][step] = float(
            2.0*(np.real(np.conj(state.coherence_acc[2,7])*inter["phase_factor"][2,7])
                 - np.real(np.conj(state.coherence_acc[7,11])*inter["phase_factor"][7,11]))
            - (abs(state.coherence_acc[2,7])**2 - abs(state.coherence_acc[7,11])**2)
        )
        obs["d_L"][step] = float(xp[25] - xp[59])
        obs["d_R"][step] = float(xp[59] - xp[29])
        obs["s2_minus_s7"][step] = float(s2 - s7)
        obs["beta25_minus_beta59"][step] = float(beta25 - beta59)
        obs["resonance_gap_L"][step] = float(Rmat[2,7] - Rmat[7,11])
        obs["resonance_gap_R"][step] = float(Rmat[7,11] - Rmat[2,11])

        aug.advance_base_state(state, inter)

    # ── Project observables onto slow subspace ──
    # Orthonormal basis for span(V_slow) via QR
    Q_slow, _ = np.linalg.qr(V_slow)
    # Projector: P = Q_slow @ Q_slow^T
    # For each observable, projected component = P @ obs (but obs is scalar per step)
    # The observable is 1D per step.  The slow subspace is a subspace of the
    # 18D state space.  The observable is a linear functional of the state.
    # We need: fraction of variance in the slow subspace over the trajectory.
    #
    # At each step, extract the fundamental state vector.
    # Project onto Q_slow:  state_proj = Q_slow @ (Q_slow.T @ state_vec)
    # The observable is a linear function of the state vector for some
    # observables (d_L, d_R come from x_prop which is a function of state).
    #
    # Simpler: fit each observable timeseries as:
    #   obs_n + offset = c * exp(-r_EMA * t_n) + faster terms
    # and report the fraction of variance explained by the slow exponential.
    # But that assumes the functional form.
    #
    # Better: at each step, extract the state, compute the projection onto
    # Q_slow, compute the observable from the projected state, and compare
    # with the actual observable.

    print("Projecting observables onto slow subspace …")
    proj_rows = []

    # Re-replay to get state vectors at each step
    with np.load(args.npz, allow_pickle=False) as data:
        state = base.load_split_state(data, args.seed)

    for step in range(fs):
        inter = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        sv = extract_fundamental(state)

        # Project state vector onto slow subspace
        sv_proj = Q_slow @ (Q_slow.T @ sv)          # slow component
        sv_fast = sv - sv_proj                        # fast complement

        # Inject projected state and compute observables
        # Save original
        snap_step = snapshot_state(state)

        # ── Observable from full state (already computed above) ──
        # Already stored in obs dict.

        # ── Observable from slow-projected state ──
        inject_fundamental(state, sv_proj)
        inter_proj = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        Rmat_p = inter_proj["R"]
        xp_p = inter_proj["x"]
        qs_p = inter_proj["q_scale"]
        s2p = caps[2]/(float(qs_p[2])+eps_sc)
        s7p = caps[7]/(float(qs_p[7])+eps_sc)
        beta25p = float(xp_p[25])*s7p/(float(qs_p[7])+eps_sc)
        beta59p = float(xp_p[59])*s7p/(float(qs_p[7])+eps_sc)

        obs_proj = {
            "d_L": float(xp_p[25] - xp_p[59]),
            "d_R": float(xp_p[59] - xp_p[29]),
            "s2_minus_s7": float(s2p - s7p),
            "beta25_minus_beta59": float(beta25p - beta59p),
            "resonance_gap_L": float(Rmat_p[2,7] - Rmat_p[7,11]),
            "resonance_gap_R": float(Rmat_p[7,11] - Rmat_p[2,11]),
        }

        restore_state(state, snap_step)
        aug.advance_base_state(state, inter)

        proj_rows.append({
            "step": step, "time": time_vec[step],
            **{f"slow_{k}": float(obs_proj[k]) for k in obs_proj},
            **{f"full_{k}": float(obs[k][step]) for k in obs},
        })

    proj_df = pd.DataFrame(proj_rows)

    # ── Variance fractions ──
    variance_rows = []
    for k in ["d_L","d_R","s2_minus_s7","beta25_minus_beta59",
              "resonance_gap_L","resonance_gap_R"]:
        full = proj_df[f"full_{k}"].values
        slow = proj_df[f"slow_{k}"].values
        # Fraction of variance in slow projection relative to full
        var_full = np.var(full)
        var_slow = np.var(slow)
        # Correlation between slow projection and full observable
        corr = np.corrcoef(slow, full)[0,1] if var_full > 1e-30 and var_slow > 1e-30 else 0

        # Also: fraction of full that comes from slow + fast + interaction
        fast = full - slow
        var_fast = np.var(fast)
        # Decomposition: var(full) = var(slow) + var(fast) + 2*cov(slow,fast)
        cov_sf = np.cov(slow, fast)[0,1] if len(slow) > 1 else 0
        frac_slow = var_slow / (var_slow + var_fast + 2*abs(cov_sf) + 1e-30)

        variance_rows.append({
            "observable": k,
            "var_full": float(var_full),
            "var_slow_projection": float(var_slow),
            "correlation_slow_full": float(corr),
            "frac_variance_slow": float(frac_slow),
        })
    var_df = pd.DataFrame(variance_rows)

    # ── Also: variable-group decomposition of slow eigenvectors ──
    var_labels = (
        [f"h_old_{i}" for i in K3_NODES]
        + [f"B_{e}" for _,_,e in K3_EDGE_LIST]
        + [f"{'C' if k%2==0 else ''}{ia}{ib}_{['re','im'][k%2]}"
           for k,(ia,ib) in enumerate(DIRECTED_PAIRS)]
    )
    decomp_rows = []
    for k in range(n_slow):
        v = V_slow[:, k]
        h_p = np.sum(np.abs(v[0:3])**2)
        B_p = np.sum(np.abs(v[3:6])**2)
        C_p = np.sum(np.abs(v[6:18])**2)
        tot = h_p + B_p + C_p + 1e-300
        decomp_rows.append({
            "mode": k, "rate": float(rates[slow_idx[k]]),
            "frac_h": float(h_p/tot), "frac_B": float(B_p/tot), "frac_C": float(C_p/tot),
        })
    decomp_df = pd.DataFrame(decomp_rows)

    # ── Pairwise overlaps ──
    omat = np.abs(V_slow.T.conj() @ V_slow)
    offdiag = [omat[i,j] for i in range(n_slow) for j in range(n_slow) if i != j]
    mean_overlap = float(np.mean(offdiag)) if offdiag else 0.0

    # ── Output ──
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)
    safe_atomic_write_csv(od/"observable_projections.csv", proj_df)
    safe_atomic_write_csv(od/"variance_fractions.csv", var_df)
    safe_atomic_write_csv(od/"eigenvector_decomposition.csv", decomp_df)

    # ── Report ──
    lines = [
        "="*70,
        "AIEF-1.4 Slow Subspace Projection",
        "="*70,
        f"r_EMA: {r_ema:.6f}   alpha: {alpha:.12g}   dt: {dt}",
        f"Slow EMA-cluster modes: {n_slow}",
        f"Effective dimension (95% SVD): {eff_dim}",
        f"Mean pairwise overlap: {mean_overlap:.4f}",
        "",
        "─"*70,
        "Observable variance captured by slow subspace:",
        "─"*70,
        f"  {'Observable':<24} {'var(slow)/var(total)':>20} {'corr(slow,full)':>16}",
        f"  {'-'*24} {'-'*20} {'-'*16}",
    ]
    for _, r in var_df.iterrows():
        lines.append(
            f"  {r['observable']:<24} {r['frac_variance_slow']:>20.4f} "
            f"{r['correlation_slow_full']:>16.6f}"
        )
    lines.append("")

    mean_cap = float(np.mean(var_df["frac_variance_slow"]))
    if mean_cap > 0.95:
        lines.append("  All measured observables are dominated by the slow subspace.")
        lines.append("  The single-rate behavior is not coincident — it reflects")
        lines.append("  a shared invariant mechanism in the linearized dynamics.")
    elif mean_cap > 0.80:
        lines.append("  Most observables are primarily in the slow subspace.")
        lines.append("  Some fast-subspace contamination exists but is secondary.")
    else:
        lines.append("  Observables have significant fast-subspace components.")
        lines.append("  Single-rate inheritance is not explained by this subspace alone.")

    lines.extend([
        "",
        "─"*70,
        "Variable-group composition of slow eigenvectors:",
        "─"*70,
        f"  {'Mode':>5} {'rate':>10} {'% h_old':>10} {'% B':>10} {'% C':>10}",
        f"  {'-'*5} {'-'*10} {'-'*10} {'-'*10} {'-'*10}",
    ])
    for _, r in decomp_df.iterrows():
        lines.append(
            f"  {r['mode']:>5} {r['rate']:>10.6f} "
            f"{r['frac_h']*100:>10.1f} {r['frac_B']*100:>10.1f} {r['frac_C']*100:>10.1f}"
        )
    mh, mB, mC = [float(np.mean(decomp_df[c])) for c in ["frac_h","frac_B","frac_C"]]
    lines.append(
        f"  {'mean':>5} {'':>10} {mh*100:>10.1f} {mB*100:>10.1f} {mC*100:>10.1f}"
    )

    if mC > 0.5:
        lines.append("  → EMA/coherence variables dominate the slow subspace.")
    elif mh > 0.5:
        lines.append("  → History variables dominate the slow subspace.")
    elif mB > 0.5:
        lines.append("  → Weight variables dominate the slow subspace.")

    lines.extend([
        "",
        "─"*70,
        "SVD of slow eigenvector stack:",
        "─"*70,
        f"  {'Index':>6} {'Singular value':>16} {'Cumulative %':>14}",
        f"  {'-'*6} {'-'*16} {'-'*14}",
    ])
    for i in range(len(S)):
        lines.append(
            f"  {i:>6} {S[i]:>16.6e} {cumvar[i]*100:>14.1f}"
        )
    lines.extend([
        "",
        f"  Effective rank (95%): {eff_dim}/{n_slow}",
    ])

    if eff_dim == 1:
        lines.append("  The slow subspace is effectively rank-1.")
        lines.append("  A single slow mechanism governs all observables.")
    elif eff_dim <= 2:
        lines.append(f"  Low effective dimension ({eff_dim}).")
        lines.append("  One or two distinct slow mechanisms.")
    else:
        lines.append(f"  Genuinely {eff_dim}-dimensional.")
        lines.append("  Multiple independent slow directions exist.")

    report = "\n".join(lines)
    safe_atomic_write_text(od/"slow_subspace_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 slow subspace projection",
        "seed": args.seed,
        "parameters": {"dt":dt, "r_EMA":r_ema, "alpha":alpha, "perturbation":pert},
        "n_slow_modes": n_slow, "effective_slow_dim": eff_dim,
        "mean_pairwise_overlap": mean_overlap,
        "mean_observable_slow_fraction": mean_cap,
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
