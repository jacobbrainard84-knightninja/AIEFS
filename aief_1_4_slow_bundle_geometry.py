#!/usr/bin/env python3

"""
AIEF-1.4 Slow Bundle Internal Geometry

Internal structure of the compressed slow operator:
  T_slow = Q_slow^T · J_full · Q_slow   (7×7)

Questions:
  - Is T_slow approximately diagonal, block-diagonal, or fully mixed?
  - Is it nearly normal?  Nearly a scalar multiple of identity?
  - Does Schur decomposition reveal hierarchy (upper triangular)?
  - What is the ratio ‖off-diagonal‖ / ‖diagonal‖?

No replay needed — uses the already-computed Jacobian and slow basis.
"""

from __future__ import annotations

import argparse, hashlib, json, math, os, sys, tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import linalg as la

DEFAULT_RUN_HASH = "5a9f093a2fe0"
DEFAULT_NPZ = f"runs/{DEFAULT_RUN_HASH}/AIEF_1_4_{DEFAULT_RUN_HASH}_branch_diagnostics.npz"
DEFAULT_MANIFEST = f"runs/{DEFAULT_RUN_HASH}/manifest.json"
DEFAULT_OUTPUT_DIR = "aief_1_4_slow_bundle_geometry"
DEFAULT_SEED = "4619122171158768524"
DEFAULT_DT = 0.01
DEFAULT_SCALE_EPSILON = 1e-12
DEFAULT_PERTURBATION = 1e-8

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

    snap_fs = snapshot_state(state)
    inter_fs = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
    aug.advance_base_state(state, inter_fs)
    v_after = extract_fundamental(state)
    n_vars = len(v_after)

    print(f"Building {n_vars}×{n_vars} Jacobian …")
    J_full = np.zeros((n_vars, n_vars))
    for col in range(n_vars):
        restore_state(state, snap_fs)
        vc = extract_fundamental(state)
        delta = pert * max(1.0, abs(vc[col]))
        vc[col] += delta
        inject_fundamental(state, vc)
        inter_p = aug.base_intermediates(state, model, caps, A, edges_mat, eps_sc)
        aug.advance_base_state(state, inter_p)
        vp = extract_fundamental(state)
        J_full[:, col] = (vp - v_after)/delta
        if (col+1) % 6 == 0: print(f"  column {col+1}/{n_vars}")

    # ── Slow subspace ──
    evals, evecs_r = np.linalg.eig(J_full)
    abs_evals = np.abs(evals)
    rates = -np.log(np.maximum(abs_evals, 1e-300))/dt
    slow_mask = (rates > r_ema*0.99) & (rates < r_ema*1.01) & (abs_evals < 1.0)
    slow_idx = np.where(slow_mask)[0]
    Q_slow = build_real_slow_basis(evecs_r, slow_idx)
    d = Q_slow.shape[1]
    print(f"  Slow subspace dimension: {d}")

    # ── Compress J_full onto Q_slow ──
    T = Q_slow.T @ J_full @ Q_slow   # d×d real matrix

    # ── Diagnostics ──
    # 1. Diagonal dominance
    diag = np.diag(np.diag(T))
    offdiag = T - diag
    diag_norm = float(np.linalg.norm(diag, 'fro'))
    off_norm  = float(np.linalg.norm(offdiag, 'fro'))
    total_norm = float(np.linalg.norm(T, 'fro'))
    ratio = off_norm / (diag_norm + 1e-30)

    # 2. Nearness to scalar multiple of identity
    mean_diag = float(np.mean(np.diag(T)))
    scalar_part = mean_diag * np.eye(d)
    dev_from_scalar = float(np.linalg.norm(T - scalar_part, 'fro'))
    frac_scalar = 1.0 - dev_from_scalar / (total_norm + 1e-30)

    # 3. Normality: ‖T T^T − T^T T‖
    nonnorm = float(np.linalg.norm(T @ T.T - T.T @ T, 'fro'))
    norm_T = float(np.linalg.norm(T, 'fro'))
    nonnorm_ratio = nonnorm / (norm_T**2 + 1e-30)

    # 4. Schur decomposition
    Schur_T, Schur_U = la.schur(T)   # T = U S U^T, S upper quasi-triangular
    # Measure upper-triangular character
    S_lower = np.tril(Schur_T, -1)
    S_diag  = np.diag(np.diag(Schur_T))
    S_upper = np.triu(Schur_T, 1)
    lower_norm = float(np.linalg.norm(S_lower, 'fro'))
    diag_norm_s = float(np.linalg.norm(S_diag, 'fro'))
    upper_norm_s = float(np.linalg.norm(S_upper, 'fro'))
    quasi_tri = lower_norm / (diag_norm_s + upper_norm_s + 1e-30)

    # 5. Principal angles between Q_slow and C-coordinate plane (indices 6..17)
    C_basis = np.zeros((n_vars, 12))
    C_basis[6:18, :] = np.eye(12)
    U_pa, S_pa, Vh_pa = np.linalg.svd(Q_slow.T @ C_basis, full_matrices=False)
    angles = np.arccos(np.clip(S_pa, 0.0, 1.0))
    angle_deg = angles * 180.0 / np.pi

    # 6. Frobenius projection norms (basis-independent)
    proj_h2 = float(np.sum(Q_slow[0:3, :]**2))
    proj_B2 = float(np.sum(Q_slow[3:6, :]**2))
    proj_C2 = float(np.sum(Q_slow[6:18, :]**2))
    total2  = proj_h2 + proj_B2 + proj_C2
    frac_h_proj = proj_h2 / (total2 + 1e-30)
    frac_B_proj = proj_B2 / (total2 + 1e-30)
    frac_C_proj = proj_C2 / (total2 + 1e-30)

    # ── Output ──
    od = Path(args.output_dir); od.mkdir(parents=True, exist_ok=True)

    # Save T entries
    t_rows = []
    for i in range(d):
        for j in range(d):
            t_rows.append({"i": i, "j": j, "T_ij": float(T[i,j])})
    pd.DataFrame(t_rows).to_csv(od/"compressed_operator_entries.csv", index=False)

    # ── Report ──
    lines = [
        "="*70,
        "AIEF-1.4 Slow Bundle Internal Geometry",
        "="*70,
        f"r_EMA: {r_ema:.6f}   slow subspace dim: {d}",
        f"alpha: {alpha:.12g}   mean(diag(T)): {mean_diag:.12g}",
        "",
        "T = Q_slow^T · J_full · Q_slow   (compressed slow operator, {d}×{d})".format(d=d),
        "",
        "─"*70,
        f"Global structure diagnostics ({d}×{d}):",
        "─"*70,
        f"  ‖T‖_F                              = {total_norm:.6e}",
        f"  ‖off-diag‖_F / ‖diag‖_F           = {ratio:.6e}",
        f"  Nearly scalar × I?  fraction       = {frac_scalar:.4f}",
        f"  Non-normality  ‖TT^T − T^TT‖/‖T‖² = {nonnorm_ratio:.6e}",
        f"  Schur lower-tri / (diag+upper)     = {quasi_tri:.6e}",
        "",
    ]

    if ratio < 1e-6:
        lines.append("  → T is essentially diagonal.  Slow modes are decoupled.")
    elif ratio < 0.01:
        lines.append("  → T is strongly diagonally dominant.")
    elif ratio < 0.1:
        lines.append("  → Moderate off-diagonal coupling among slow modes.")
    else:
        lines.append("  → Significant off-diagonal structure.")

    if nonnorm_ratio < 1e-12:
        lines.append("  → T is normal to machine precision.")
    elif nonnorm_ratio < 1e-6:
        lines.append("  → T is very nearly normal.")
    elif nonnorm_ratio < 1e-3:
        lines.append("  → Weak non-normality detected.")
    else:
        lines.append("  → T is significantly non-normal.")

    if frac_scalar > 0.9999:
        lines.append("  → T ≈ α·I.  All slow modes are isotropic.")
    elif frac_scalar > 0.99:
        lines.append("  → T is close to scalar × I; slow modes nearly isotropic.")
    elif frac_scalar > 0.9:
        lines.append("  → Moderate deviation from isotropy.")
    else:
        lines.append("  → Slow modes are anisotropic — internal hierarchy exists.")

    if quasi_tri < 1e-6:
        lines.append("  → Schur form is essentially upper triangular (no 2×2 blocks).")
    elif quasi_tri < 0.01:
        lines.append("  → Schur form is quasi-triangular (small complex-conjugate blocks).")
    else:
        lines.append("  → Significant lower-triangular components in Schur form.")

    # Principal angles
    lines.extend([
        "",
        "─"*70,
        "Principal angles: slow subspace vs. C-coordinate plane (12-dim):",
        "─"*70,
    ])
    for i in range(min(d, len(angles))):
        lines.append(f"  angle[{i}] = {angles[i]:.6e} rad = {angle_deg[i]:.4f}°")
    lines.append("")
    if np.max(angles) < 0.001:
        lines.append("  → All principal angles < 0.001 rad (< 0.06°).")
        lines.append("    The slow subspace is essentially contained in the C plane.")
    elif np.max(angles) < 0.01:
        lines.append("  → Max angle < 0.01 rad (< 0.6°).  Strongly C-aligned.")
    elif np.max(angles) < 0.1:
        lines.append(f"  → Max angle = {np.max(angle_deg):.2f}°.  Mostly C, some B/h component.")
    else:
        lines.append(f"  → Max angle = {np.max(angle_deg):.1f}°.  Non-negligible B/h mixing.")

    # Frobenius projection norms
    lines.extend([
        "",
        "─"*70,
        "Frobenius projection norms (basis-independent):",
        "─"*70,
        f"  ‖Π_h Q_slow‖_F² / d  = {frac_h_proj:.6e}",
        f"  ‖Π_B Q_slow‖_F² / d  = {frac_B_proj:.6e}",
        f"  ‖Π_C Q_slow‖_F² / d  = {frac_C_proj:.6e}",
        "",
    ])
    if frac_C_proj > 0.999999:
        lines.append("  → The slow subspace is essentially pure C (6+ nines).")
    elif frac_C_proj > 0.9999:
        lines.append("  → C-dominant at 4+ nines.  B contribution at ~10⁻⁴ level.")
    elif frac_C_proj > 0.99:
        lines.append(f"  → C-dominant.  B+h = {(frac_h_proj+frac_B_proj)*100:.2f}%.")
    else:
        lines.append(f"  → Mixed.  h={frac_h_proj*100:.1f}% B={frac_B_proj*100:.1f}% C={frac_C_proj*100:.1f}%")

    # Eigenvalues of T for reference
    ev_T = np.linalg.eigvals(T)
    rates_T = -np.log(np.maximum(np.abs(ev_T), 1e-300))/dt
    lines.extend([
        "",
        "─"*70,
        "Compressed eigenvalues (continuous-time rates):",
        "─"*70,
        f"  {sorted(rates_T)[:6]}",
        f"  mean = {np.mean(rates_T):.6f},  std = {np.std(rates_T):.6e}",
        "",
        f"  Reference: r_EMA = {r_ema:.6f}",
    ])

    report = "\n".join(lines)
    safe_atomic_write_text(od/"slow_bundle_geometry_report.txt", report)

    mf = {
        "analysis": "AIEF-1.4 slow bundle internal geometry",
        "seed": args.seed,
        "slow_dim": d,
        "diag_ratio": ratio,
        "scalar_fraction": frac_scalar,
        "nonnormality": nonnorm_ratio,
        "schur_quasi_tri": quasi_tri,
        "max_principal_angle_deg": float(np.max(angle_deg)),
        "mean_compressed_rate": float(np.mean(rates_T)),
    }
    safe_atomic_write_text(od/"analysis_manifest.json",
                           json.dumps(mf, indent=2)+"\n")
    print(report)
    print(f"\nDone. → {od.resolve()}")

if __name__ == "__main__":
    main()
